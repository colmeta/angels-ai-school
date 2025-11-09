"""
Bulk Operations Service - Mass data operations for efficiency
Handles bulk imports, bulk marking, bulk messaging, etc.

Examples:
- "Mark all Class 5A as present" → Marks entire class
- Upload CSV → Import 100+ students at once
- Upload Excel → Record grades for all students
- "Send message to all parents" → Notify everyone
"""
import csv
import io
import re
from typing import Dict, Any, List, Optional
from datetime import date
from uuid import uuid4

from api.services.database import get_db_manager
from api.services.notifications import NotificationService
from api.services.command_intelligence import CommandIntelligenceService


class BulkOperationsService:
    """Handle bulk operations for maximum efficiency"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
        self.notification_service = NotificationService()
    
    # ============================================================================
    # BULK ATTENDANCE
    # ============================================================================
    
    async def mark_class_attendance(
        self,
        class_name: str,
        status: str = "present",
        date_str: Optional[str] = None,
        exclude_students: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Mark attendance for an entire class
        
        Args:
            class_name: Class name (e.g., "Class 5A", "Primary 3")
            status: Attendance status (present/absent/late)
            date_str: Date (defaults to today)
            exclude_students: Student IDs to exclude
        
        Returns:
            Summary with count of students marked
        """
        attendance_date = date_str or date.today().isoformat()
        exclude_students = exclude_students or []
        
        # Get all students in class
        query = """
            SELECT id, first_name, last_name
            FROM students
            WHERE school_id = %s AND class_name = %s AND status = 'active'
        """
        params = [self.school_id, class_name]
        
        if exclude_students:
            placeholders = ','.join(['%s'] * len(exclude_students))
            query += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_students)
        
        students = self.db.execute_query(query, tuple(params), fetch=True)
        
        if not students:
            return {
                "success": False,
                "error": f"No students found in {class_name}"
            }
        
        # Mark attendance for all students
        marked_count = 0
        parent_notifications = 0
        
        for student in students:
            # Insert/update attendance
            attendance_id = str(uuid4())
            self.db.execute_query(
                """
                INSERT INTO attendance (id, school_id, student_id, date, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (student_id, date)
                DO UPDATE SET status = EXCLUDED.status, updated_at = CURRENT_TIMESTAMP
                """,
                (attendance_id, self.school_id, student["id"], attendance_date, status)
            )
            marked_count += 1
            
            # Notify parents
            parents = self.db.execute_query(
                """
                SELECT p.id FROM parents p
                JOIN student_parents sp ON sp.parent_id = p.id
                WHERE sp.student_id = %s
                """,
                (student["id"],),
                fetch=True
            )
            
            for parent in parents:
                await self.notification_service.notify_parent_attendance(
                    school_id=self.school_id,
                    student_id=student["id"],
                    parent_id=parent["id"],
                    status=status,
                    date=attendance_date
                )
                parent_notifications += 1
        
        return {
            "success": True,
            "action": "bulk_attendance_marked",
            "class_name": class_name,
            "status": status,
            "date": attendance_date,
            "students_marked": marked_count,
            "parents_notified": parent_notifications
        }
    
    async def mark_all_present_except(
        self,
        class_name: str,
        absent_students: List[str],
        date_str: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark all students present except specified ones
        
        Args:
            class_name: Class name
            absent_students: List of student names/IDs to mark as absent
            date_str: Date (defaults to today)
        """
        # Mark everyone present first
        present_result = await self.mark_class_attendance(
            class_name=class_name,
            status="present",
            date_str=date_str
        )
        
        # Mark specified students as absent
        absent_count = 0
        for student_identifier in absent_students:
            # Find student by name or ID
            students = self.db.execute_query(
                """
                SELECT id FROM students
                WHERE school_id = %s
                AND class_name = %s
                AND (id = %s OR CONCAT(first_name, ' ', last_name) ILIKE %s)
                LIMIT 1
                """,
                (self.school_id, class_name, student_identifier, f"%{student_identifier}%"),
                fetch=True
            )
            
            if students:
                student_id = students[0]["id"]
                attendance_id = str(uuid4())
                self.db.execute_query(
                    """
                    INSERT INTO attendance (id, school_id, student_id, date, status)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (student_id, date)
                    DO UPDATE SET status = 'absent', updated_at = CURRENT_TIMESTAMP
                    """,
                    (attendance_id, self.school_id, student_id, date_str or date.today().isoformat(), "absent")
                )
                absent_count += 1
                
                # Notify parents of absent students
                parents = self.db.execute_query(
                    "SELECT p.id FROM parents p JOIN student_parents sp ON sp.parent_id = p.id WHERE sp.student_id = %s",
                    (student_id,),
                    fetch=True
                )
                for parent in parents:
                    await self.notification_service.notify_parent_attendance(
                        school_id=self.school_id,
                        student_id=student_id,
                        parent_id=parent["id"],
                        status="absent",
                        date=date_str or date.today().isoformat()
                    )
        
        return {
            "success": True,
            "action": "bulk_attendance_except",
            "class_name": class_name,
            "students_marked_present": present_result.get("students_marked", 0) - absent_count,
            "students_marked_absent": absent_count,
            "total_students": present_result.get("students_marked", 0)
        }
    
    # ============================================================================
    # BULK STUDENT IMPORT
    # ============================================================================
    
    async def import_students_from_csv(
        self,
        csv_content: str,
        update_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Import students from CSV file
        
        CSV Format:
        first_name,last_name,date_of_birth,gender,class_name,admission_number
        John,Doe,2010-05-15,Male,Class 5A,2024001
        Mary,Smith,2011-03-20,Female,Class 5A,2024002
        
        Args:
            csv_content: CSV file content as string
            update_existing: Update if admission number exists
        
        Returns:
            Summary with counts of created/updated/failed
        """
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        created = 0
        updated = 0
        failed = []
        
        for row in reader:
            try:
                # Validate required fields
                required = ["first_name", "last_name", "admission_number"]
                missing = [f for f in required if not row.get(f)]
                if missing:
                    failed.append({
                        "row": row,
                        "error": f"Missing fields: {', '.join(missing)}"
                    })
                    continue
                
                # Check if student exists
                existing = self.db.execute_query(
                    "SELECT id FROM students WHERE school_id = %s AND admission_number = %s",
                    (self.school_id, row["admission_number"]),
                    fetch=True
                )
                
                if existing and not update_existing:
                    failed.append({
                        "row": row,
                        "error": "Student already exists"
                    })
                    continue
                
                if existing:
                    # Update existing student
                    self.db.execute_query(
                        """
                        UPDATE students
                        SET first_name = %s, last_name = %s, date_of_birth = %s,
                            gender = %s, class_name = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (
                            row["first_name"],
                            row["last_name"],
                            row.get("date_of_birth"),
                            row.get("gender"),
                            row.get("class_name"),
                            existing[0]["id"]
                        )
                    )
                    updated += 1
                else:
                    # Create new student
                    student_id = str(uuid4())
                    self.db.execute_query(
                        """
                        INSERT INTO students (
                            id, school_id, first_name, last_name, date_of_birth,
                            gender, class_name, admission_number, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active')
                        """,
                        (
                            student_id,
                            self.school_id,
                            row["first_name"],
                            row["last_name"],
                            row.get("date_of_birth"),
                            row.get("gender"),
                            row.get("class_name"),
                            row["admission_number"]
                        )
                    )
                    created += 1
                    
            except Exception as e:
                failed.append({
                    "row": row,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "action": "bulk_student_import",
            "created": created,
            "updated": updated,
            "failed": len(failed),
            "failed_details": failed[:10]  # First 10 failures
        }
    
    # ============================================================================
    # BULK GRADING
    # ============================================================================
    
    async def import_grades_from_csv(
        self,
        csv_content: str,
        assessment_name: str,
        subject: str,
        max_marks: float = 100
    ) -> Dict[str, Any]:
        """
        Import grades from CSV
        
        CSV Format:
        admission_number,marks
        2024001,85
        2024002,92
        
        Args:
            csv_content: CSV content
            assessment_name: Name of assessment/exam
            subject: Subject name
            max_marks: Maximum marks
        """
        # Create assessment
        assessment_id = str(uuid4())
        self.db.execute_query(
            """
            INSERT INTO assessments (id, school_id, name, subject, max_marks, date)
            VALUES (%s, %s, %s, %s, %s, CURRENT_DATE)
            """,
            (assessment_id, self.school_id, assessment_name, subject, max_marks)
        )
        
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        recorded = 0
        failed = []
        parent_notifications = 0
        
        for row in reader:
            try:
                # Find student
                students = self.db.execute_query(
                    "SELECT id, first_name, last_name FROM students WHERE school_id = %s AND admission_number = %s",
                    (self.school_id, row["admission_number"]),
                    fetch=True
                )
                
                if not students:
                    failed.append({"row": row, "error": "Student not found"})
                    continue
                
                student = students[0]
                marks = float(row["marks"])
                grade = self._calculate_grade(marks, max_marks)
                
                # Record result
                result_id = str(uuid4())
                self.db.execute_query(
                    """
                    INSERT INTO assessment_results (id, assessment_id, student_id, marks_obtained, grade)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (result_id, assessment_id, student["id"], marks, grade)
                )
                recorded += 1
                
                # Notify parents
                parents = self.db.execute_query(
                    "SELECT p.id FROM parents p JOIN student_parents sp ON sp.parent_id = p.id WHERE sp.student_id = %s",
                    (student["id"],),
                    fetch=True
                )
                
                for parent in parents:
                    await self.notification_service.send_notification(
                        school_id=self.school_id,
                        recipient_id=parent["id"],
                        recipient_type="parent",
                        notification_type="academic",
                        title=f"New Grade: {assessment_name}",
                        message=f"{student['first_name']} scored {marks}/{max_marks} ({grade}) in {subject}",
                        channels=["app", "email"]
                    )
                    parent_notifications += 1
                    
            except Exception as e:
                failed.append({"row": row, "error": str(e)})
        
        return {
            "success": True,
            "action": "bulk_grade_import",
            "assessment": assessment_name,
            "subject": subject,
            "recorded": recorded,
            "failed": len(failed),
            "parents_notified": parent_notifications,
            "failed_details": failed[:10]
        }
    
    # ============================================================================
    # BULK MESSAGING
    # ============================================================================
    
    async def send_bulk_message(
        self,
        recipient_type: str,
        title: str,
        message: str,
        filters: Optional[Dict] = None,
        channels: List[str] = None
    ) -> Dict[str, Any]:
        """
        Send message to multiple recipients
        
        Args:
            recipient_type: "all_parents", "all_teachers", "all_students", "class_parents"
            title: Message title
            message: Message content
            filters: Additional filters (e.g., {"class_name": "Class 5A"})
            channels: Notification channels (default: ["app", "email"])
        """
        channels = channels or ["app", "email"]
        filters = filters or {}
        
        # Get recipients based on type
        if recipient_type == "all_parents":
            recipients = self.db.execute_query(
                "SELECT id, first_name, last_name FROM parents WHERE school_id = %s",
                (self.school_id,),
                fetch=True
            )
            recipient_role = "parent"
            
        elif recipient_type == "all_teachers":
            recipients = self.db.execute_query(
                "SELECT id, first_name, last_name FROM teachers WHERE school_id = %s",
                (self.school_id,),
                fetch=True
            )
            recipient_role = "teacher"
            
        elif recipient_type == "all_students":
            recipients = self.db.execute_query(
                "SELECT id, first_name, last_name FROM students WHERE school_id = %s AND status = 'active'",
                (self.school_id,),
                fetch=True
            )
            recipient_role = "student"
            
        elif recipient_type == "class_parents":
            class_name = filters.get("class_name")
            if not class_name:
                return {"success": False, "error": "class_name required for class_parents"}
            
            recipients = self.db.execute_query(
                """
                SELECT DISTINCT p.id, p.first_name, p.last_name
                FROM parents p
                JOIN student_parents sp ON sp.parent_id = p.id
                JOIN students s ON s.id = sp.student_id
                WHERE s.school_id = %s AND s.class_name = %s
                """,
                (self.school_id, class_name),
                fetch=True
            )
            recipient_role = "parent"
        else:
            return {"success": False, "error": f"Unknown recipient_type: {recipient_type}"}
        
        # Send to all recipients
        sent_count = 0
        for recipient in recipients:
            await self.notification_service.send_notification(
                school_id=self.school_id,
                recipient_id=recipient["id"],
                recipient_type=recipient_role,
                notification_type="announcement",
                title=title,
                message=message,
                channels=channels,
                priority="normal"
            )
            sent_count += 1
        
        return {
            "success": True,
            "action": "bulk_message_sent",
            "recipient_type": recipient_type,
            "title": title,
            "recipients": sent_count,
            "channels": channels
        }
    
    # ============================================================================
    # HELPERS
    # ============================================================================
    
    def _calculate_grade(self, marks: float, max_marks: float) -> str:
        """Calculate grade from marks"""
        percentage = (marks / max_marks) * 100
        
        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B+"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"


def get_bulk_service(school_id: str) -> BulkOperationsService:
    """Helper to get bulk operations service instance"""
    return BulkOperationsService(school_id)
