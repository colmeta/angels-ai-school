"""
Homework Tracking Service
Homework assignments, submissions, grading, completion tracking
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.services.database import get_db_manager


class HomeworkService:
    """Service for homework management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # HOMEWORK ASSIGNMENTS
    # ============================================================================
    
    def create_assignment(
        self,
        teacher_id: str,
        subject: str,
        class_name: str,
        title: str,
        description: str,
        assigned_date: str,
        due_date: str,
        total_marks: int = 100
    ) -> Dict[str, Any]:
        """Create homework assignment"""
        query = """
        INSERT INTO homework_assignments (
            school_id, teacher_id, subject, class_name, title,
            description, assigned_date, due_date, total_marks
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, teacher_id, subject, class_name, title,
             description, assigned_date, due_date, total_marks),
            fetch=True
        )
        
        # Notify students (integrate with NotificationService)
        # This would send notifications to all students in the class
        
        return {
            "success": True,
            "assignment_id": result[0]['id'],
            "class_name": class_name,
            "subject": subject,
            "due_date": due_date
        }
    
    def get_assignments_for_class(
        self,
        class_name: str,
        subject: Optional[str] = None,
        include_past: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all assignments for a class"""
        query = """
        SELECT 
            ha.id,
            ha.subject,
            ha.title,
            ha.description,
            ha.assigned_date,
            ha.due_date,
            ha.total_marks,
            t.first_name as teacher_first_name,
            t.last_name as teacher_last_name
        FROM homework_assignments ha
        JOIN teachers t ON t.id = ha.teacher_id
        WHERE ha.school_id = %s AND ha.class_name = %s
        """
        
        params = [self.school_id, class_name]
        
        if subject:
            query += " AND ha.subject = %s"
            params.append(subject)
        
        if not include_past:
            query += " AND ha.due_date >= CURRENT_DATE"
        
        query += " ORDER BY ha.due_date ASC"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_assignment_by_id(self, assignment_id: str) -> Optional[Dict[str, Any]]:
        """Get assignment details"""
        query = """
        SELECT 
            id,
            teacher_id,
            subject,
            class_name,
            title,
            description,
            assigned_date,
            due_date,
            total_marks
        FROM homework_assignments
        WHERE id = %s
        """
        
        result = self.db.execute_query(query, (assignment_id,), fetch=True)
        return result[0] if result else None
    
    # ============================================================================
    # HOMEWORK SUBMISSIONS
    # ============================================================================
    
    def submit_homework(
        self,
        assignment_id: str,
        student_id: str,
        submission_text: Optional[str] = None,
        attachment_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Student submits homework"""
        # Check if assignment is still open
        assignment = self.get_assignment_by_id(assignment_id)
        
        if not assignment:
            return {"success": False, "error": "Assignment not found"}
        
        submission_date = datetime.now().date()
        due_date = assignment['due_date']
        
        is_late = submission_date > due_date
        
        query = """
        INSERT INTO homework_submissions (
            school_id, assignment_id, student_id, submission_text,
            attachment_url, submitted_at, is_late
        ) VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
        ON CONFLICT (assignment_id, student_id) DO UPDATE
        SET submission_text = EXCLUDED.submission_text,
            attachment_url = EXCLUDED.attachment_url,
            submitted_at = CURRENT_TIMESTAMP,
            is_late = EXCLUDED.is_late
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, assignment_id, student_id, submission_text,
             attachment_url, is_late),
            fetch=True
        )
        
        return {
            "success": True,
            "submission_id": result[0]['id'],
            "assignment_id": assignment_id,
            "student_id": student_id,
            "is_late": is_late
        }
    
    def grade_submission(
        self,
        submission_id: str,
        marks_obtained: int,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Teacher grades homework submission"""
        query = """
        UPDATE homework_submissions
        SET marks_obtained = %s,
            feedback = %s,
            graded_at = CURRENT_TIMESTAMP,
            status = 'graded'
        WHERE id = %s
        """
        
        self.db.execute_query(query, (marks_obtained, feedback, submission_id))
        
        # Notify student (integrate with NotificationService)
        
        return {
            "success": True,
            "submission_id": submission_id,
            "marks_obtained": marks_obtained
        }
    
    def get_submissions_for_assignment(
        self,
        assignment_id: str
    ) -> List[Dict[str, Any]]:
        """Get all submissions for an assignment"""
        query = """
        SELECT 
            hs.id,
            hs.student_id,
            hs.submitted_at,
            hs.is_late,
            hs.marks_obtained,
            hs.status,
            s.first_name,
            s.last_name
        FROM homework_submissions hs
        JOIN students s ON s.id = hs.student_id
        WHERE hs.assignment_id = %s
        ORDER BY hs.submitted_at ASC
        """
        
        return self.db.execute_query(query, (assignment_id,), fetch=True)
    
    def get_student_submissions(
        self,
        student_id: str,
        include_graded: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all submissions for a student"""
        query = """
        SELECT 
            hs.id,
            hs.assignment_id,
            hs.submitted_at,
            hs.is_late,
            hs.marks_obtained,
            hs.feedback,
            hs.status,
            ha.subject,
            ha.title,
            ha.due_date,
            ha.total_marks
        FROM homework_submissions hs
        JOIN homework_assignments ha ON ha.id = hs.assignment_id
        WHERE hs.student_id = %s
        """
        
        if not include_graded:
            query += " AND hs.status = 'pending'"
        
        query += " ORDER BY ha.due_date DESC"
        
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    def get_pending_submissions(self, assignment_id: str) -> List[Dict[str, Any]]:
        """Get students who submitted but not yet graded"""
        query = """
        SELECT 
            hs.id,
            hs.student_id,
            hs.submitted_at,
            s.first_name,
            s.last_name
        FROM homework_submissions hs
        JOIN students s ON s.id = hs.student_id
        WHERE hs.assignment_id = %s
        AND hs.status = 'pending'
        ORDER BY hs.submitted_at ASC
        """
        
        return self.db.execute_query(query, (assignment_id,), fetch=True)
    
    def get_missing_submissions(self, assignment_id: str) -> List[Dict[str, Any]]:
        """Get students who haven't submitted homework"""
        assignment = self.get_assignment_by_id(assignment_id)
        
        if not assignment:
            return []
        
        query = """
        SELECT 
            s.id,
            s.first_name,
            s.last_name,
            s.class_name
        FROM students s
        WHERE s.school_id = %s
        AND s.class_name = %s
        AND s.status = 'active'
        AND NOT EXISTS (
            SELECT 1
            FROM homework_submissions hs
            WHERE hs.student_id = s.id
            AND hs.assignment_id = %s
        )
        ORDER BY s.first_name
        """
        
        return self.db.execute_query(
            query,
            (self.school_id, assignment['class_name'], assignment_id),
            fetch=True
        )
    
    # ============================================================================
    # ANALYTICS & REPORTS
    # ============================================================================
    
    def get_homework_completion_rate(
        self,
        class_name: str,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get homework completion rate for a class"""
        query = """
        SELECT 
            ha.id as assignment_id,
            ha.title,
            ha.subject,
            ha.due_date,
            COUNT(DISTINCT s.id) as total_students,
            COUNT(DISTINCT hs.student_id) as submitted_count,
            COUNT(DISTINCT CASE WHEN hs.is_late = false THEN hs.student_id END) as on_time_count
        FROM homework_assignments ha
        CROSS JOIN students s
        LEFT JOIN homework_submissions hs ON hs.assignment_id = ha.id AND hs.student_id = s.id
        WHERE ha.school_id = %s
        AND ha.class_name = %s
        AND s.class_name = %s
        AND s.status = 'active'
        """
        
        params = [self.school_id, class_name, class_name]
        
        if subject:
            query += " AND ha.subject = %s"
            params.append(subject)
        
        query += """
        GROUP BY ha.id, ha.title, ha.subject, ha.due_date
        ORDER BY ha.due_date DESC
        """
        
        data = self.db.execute_query(query, tuple(params), fetch=True)
        
        # Calculate percentages
        for row in data:
            total = row['total_students']
            if total > 0:
                row['completion_percentage'] = round((row['submitted_count'] / total) * 100, 1)
                row['on_time_percentage'] = round((row['on_time_count'] / total) * 100, 1)
            else:
                row['completion_percentage'] = 0
                row['on_time_percentage'] = 0
        
        return {
            "success": True,
            "class_name": class_name,
            "assignments": data
        }
    
    def get_student_homework_performance(self, student_id: str) -> Dict[str, Any]:
        """Get homework performance for a student"""
        query = """
        SELECT 
            COUNT(*) as total_assignments,
            COUNT(CASE WHEN hs.submitted_at IS NOT NULL THEN 1 END) as submitted,
            COUNT(CASE WHEN hs.is_late = false THEN 1 END) as on_time,
            ROUND(AVG(CASE WHEN hs.marks_obtained IS NOT NULL THEN 
                (hs.marks_obtained::DECIMAL / ha.total_marks) * 100 
            END), 1) as average_percentage
        FROM homework_assignments ha
        LEFT JOIN homework_submissions hs ON hs.assignment_id = ha.id AND hs.student_id = %s
        WHERE ha.school_id = %s
        AND ha.class_name = (SELECT class_name FROM students WHERE id = %s)
        """
        
        result = self.db.execute_query(query, (student_id, self.school_id, student_id), fetch=True)
        
        return {
            "success": True,
            "student_id": student_id,
            "statistics": result[0] if result else {}
        }


def get_homework_service(school_id: str) -> HomeworkService:
    """Helper to get homework service instance"""
    return HomeworkService(school_id)
