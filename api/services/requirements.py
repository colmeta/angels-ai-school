"""
School Requirements Service
Handles school supplies, trip fees, and other non-tuition requirements
Tracks what students bring/pay (toilet paper, brooms, etc.)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from api.services.database import get_db_manager
from api.services.notifications import NotificationService


class SchoolRequirementsService:
    """Service for managing school requirements and student submissions"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
        self.notification_service = NotificationService()
    
    # ============================================================================
    # REQUIREMENT MANAGEMENT
    # ============================================================================
    
    def create_requirement(
        self,
        name: str,
        requirement_type: str,  # supply, fee, both
        category_id: Optional[str] = None,
        description: Optional[str] = None,
        quantity_required: Optional[int] = None,
        unit: Optional[str] = None,
        amount_required: Optional[float] = None,
        applies_to: str = 'all_students',
        target_class: Optional[str] = None,
        due_date: Optional[str] = None,
        term: Optional[str] = None,
        is_mandatory: bool = True,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new school requirement
        
        Examples:
        - Toilet Paper: type=supply, quantity=2, unit=rolls
        - Trip Fee: type=fee, amount=20000
        - Broom: type=supply, quantity=1, unit=pieces
        """
        query = """
        INSERT INTO school_requirements (
            school_id, category_id, name, description, requirement_type,
            quantity_required, unit, amount_required, applies_to, target_class,
            due_date, term, is_mandatory, created_by
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING id, name, requirement_type, due_date
        """
        
        result = self.db.execute_query(
            query,
            (
                self.school_id, category_id, name, description, requirement_type,
                quantity_required, unit, amount_required, applies_to, target_class,
                due_date, term, is_mandatory, created_by
            ),
            fetch=True
        )
        
        requirement_id = result[0]['id']
        
        # Send notifications to parents
        self._send_requirement_notification(requirement_id, 'initial')
        
        return {
            "success": True,
            "requirement_id": requirement_id,
            "name": name,
            "type": requirement_type,
            "due_date": due_date
        }
    
    def get_requirements(
        self,
        category_id: Optional[str] = None,
        requirement_type: Optional[str] = None,
        class_name: Optional[str] = None,
        is_active: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all requirements for the school with filters"""
        query = """
        SELECT 
            sr.id,
            sr.name,
            sr.description,
            sr.requirement_type,
            sr.quantity_required,
            sr.unit,
            sr.amount_required,
            sr.currency,
            sr.applies_to,
            sr.target_class,
            sr.due_date,
            sr.term,
            sr.is_mandatory,
            rc.name as category_name,
            rcs.total_students,
            rcs.submitted_count,
            rcs.pending_count,
            rcs.completion_percentage
        FROM school_requirements sr
        LEFT JOIN requirement_categories rc ON rc.id = sr.category_id
        LEFT JOIN requirement_completion_summary rcs ON rcs.requirement_id = sr.id
        WHERE sr.school_id = %s AND sr.is_active = %s
        """
        
        params = [self.school_id, is_active]
        
        if category_id:
            query += " AND sr.category_id = %s"
            params.append(category_id)
        
        if requirement_type:
            query += " AND sr.requirement_type = %s"
            params.append(requirement_type)
        
        if class_name:
            query += " AND (sr.applies_to = 'all_students' OR sr.target_class = %s)"
            params.append(class_name)
        
        query += " ORDER BY sr.due_date ASC NULLS LAST, sr.created_at DESC"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_requirement_completion_summary(self, requirement_id: str) -> Dict[str, Any]:
        """Get detailed completion summary for a requirement"""
        query = """
        SELECT * FROM requirement_completion_summary
        WHERE requirement_id = %s
        """
        
        summary = self.db.execute_query(query, (requirement_id,), fetch=True)
        
        if not summary:
            return {"error": "Requirement not found"}
        
        # Get list of students who haven't submitted
        pending_query = """
        SELECT 
            s.id,
            s.first_name,
            s.last_name,
            s.class_name,
            s.admission_number
        FROM students s
        JOIN school_requirements sr ON sr.school_id = s.school_id
        LEFT JOIN student_requirement_submissions srs ON (
            srs.student_id = s.id AND srs.requirement_id = sr.id
        )
        WHERE 
            sr.id = %s
            AND s.status = 'active'
            AND srs.id IS NULL
            AND (
                sr.applies_to = 'all_students'
                OR (sr.applies_to = 'specific_class' AND s.class_name = sr.target_class)
            )
        ORDER BY s.class_name, s.first_name
        """
        
        pending_students = self.db.execute_query(pending_query, (requirement_id,), fetch=True)
        
        return {
            **summary[0],
            "pending_students": pending_students
        }
    
    # ============================================================================
    # STUDENT SUBMISSIONS
    # ============================================================================
    
    def submit_requirement(
        self,
        requirement_id: str,
        student_id: str,
        quantity_submitted: Optional[int] = None,
        amount_paid: Optional[float] = None,
        payment_method: Optional[str] = None,
        payment_reference: Optional[str] = None,
        submission_date: Optional[str] = None,
        condition: Optional[str] = 'new',
        notes: Optional[str] = None,
        photo_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record a student's submission (brought item or paid fee)
        
        Can be submitted by:
        - Parent (via app)
        - Teacher (manual entry)
        - Admin (bulk import)
        """
        # Verify requirement exists
        req_query = "SELECT requirement_type FROM school_requirements WHERE id = %s"
        requirement = self.db.execute_query(req_query, (requirement_id,), fetch=True)
        
        if not requirement:
            return {"success": False, "error": "Requirement not found"}
        
        requirement_type = requirement[0]['requirement_type']
        
        # Insert or update submission
        query = """
        INSERT INTO student_requirement_submissions (
            school_id, requirement_id, student_id,
            quantity_submitted, amount_paid, payment_method, payment_reference,
            submission_date, payment_date, condition, notes, photo_url
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (requirement_id, student_id)
        DO UPDATE SET
            quantity_submitted = COALESCE(EXCLUDED.quantity_submitted, student_requirement_submissions.quantity_submitted),
            amount_paid = COALESCE(EXCLUDED.amount_paid, student_requirement_submissions.amount_paid),
            payment_method = COALESCE(EXCLUDED.payment_method, student_requirement_submissions.payment_method),
            payment_reference = COALESCE(EXCLUDED.payment_reference, student_requirement_submissions.payment_reference),
            submission_date = COALESCE(EXCLUDED.submission_date, student_requirement_submissions.submission_date),
            payment_date = COALESCE(EXCLUDED.payment_date, student_requirement_submissions.payment_date),
            condition = COALESCE(EXCLUDED.condition, student_requirement_submissions.condition),
            notes = COALESCE(EXCLUDED.notes, student_requirement_submissions.notes),
            photo_url = COALESCE(EXCLUDED.photo_url, student_requirement_submissions.photo_url),
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        today = submission_date or str(date.today())
        
        result = self.db.execute_query(
            query,
            (
                self.school_id, requirement_id, student_id,
                quantity_submitted, amount_paid, payment_method, payment_reference,
                today, today, condition, notes, photo_url
            ),
            fetch=True
        )
        
        # Auto-verify fee payments (can manually verify supplies)
        if requirement_type == 'fee' and amount_paid:
            self.verify_submission(result[0]['id'], verified_by=None)
        
        return {
            "success": True,
            "submission_id": result[0]['id'],
            "requirement_id": requirement_id,
            "student_id": student_id
        }
    
    def verify_submission(
        self,
        submission_id: str,
        verified_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a submission (teacher/admin confirms item is acceptable)
        """
        query = """
        UPDATE student_requirement_submissions
        SET verified = true,
            verified_by = %s,
            verified_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING student_id, requirement_id
        """
        
        result = self.db.execute_query(query, (verified_by, submission_id), fetch=True)
        
        if result:
            return {
                "success": True,
                "submission_id": submission_id,
                "verified": True
            }
        
        return {"success": False, "error": "Submission not found"}
    
    def get_student_submissions(
        self,
        student_id: str,
        status: Optional[str] = None  # submitted, pending, overdue
    ) -> List[Dict[str, Any]]:
        """Get all requirements and their status for a student"""
        query = """
        SELECT * FROM student_requirements_status
        WHERE student_id = %s AND school_id = %s
        """
        
        params = [student_id, self.school_id]
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY due_date ASC NULLS LAST, requirement_name"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_class_submissions(
        self,
        class_name: str,
        requirement_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get submission status for entire class"""
        query = """
        SELECT 
            s.id as student_id,
            s.first_name,
            s.last_name,
            s.admission_number,
            sr.id as requirement_id,
            sr.name as requirement_name,
            sr.requirement_type,
            srs.quantity_submitted,
            srs.amount_paid,
            srs.verified,
            srs.submission_date,
            CASE 
                WHEN srs.id IS NOT NULL THEN 'submitted'
                WHEN sr.due_date < CURRENT_DATE THEN 'overdue'
                ELSE 'pending'
            END as status
        FROM students s
        CROSS JOIN school_requirements sr
        LEFT JOIN student_requirement_submissions srs ON (
            srs.student_id = s.id AND srs.requirement_id = sr.id
        )
        WHERE 
            s.school_id = %s
            AND s.class_name = %s
            AND s.status = 'active'
            AND sr.school_id = %s
            AND sr.is_active = true
            AND (sr.applies_to = 'all_students' OR sr.target_class = %s)
        """
        
        params = [self.school_id, class_name, self.school_id, class_name]
        
        if requirement_id:
            query += " AND sr.id = %s"
            params.append(requirement_id)
        
        query += " ORDER BY s.first_name, sr.name"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    # ============================================================================
    # BULK OPERATIONS
    # ============================================================================
    
    def bulk_submit_for_class(
        self,
        requirement_id: str,
        class_name: str,
        quantity_submitted: Optional[int] = None,
        amount_paid: Optional[float] = None,
        exclude_students: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Mark requirement as submitted for all students in a class
        
        Example: "Mark all Class 5A students as having brought toilet paper"
        """
        # Get all students in class
        query = """
        SELECT id FROM students
        WHERE school_id = %s AND class_name = %s AND status = 'active'
        """
        
        if exclude_students:
            query += f" AND id NOT IN ({','.join(['%s'] * len(exclude_students))})"
            params = [self.school_id, class_name] + exclude_students
        else:
            params = [self.school_id, class_name]
        
        students = self.db.execute_query(query, tuple(params), fetch=True)
        
        success_count = 0
        for student in students:
            result = self.submit_requirement(
                requirement_id=requirement_id,
                student_id=student['id'],
                quantity_submitted=quantity_submitted,
                amount_paid=amount_paid
            )
            if result.get('success'):
                success_count += 1
        
        return {
            "success": True,
            "total_students": len(students),
            "submitted_count": success_count,
            "class_name": class_name,
            "requirement_id": requirement_id
        }
    
    # ============================================================================
    # NOTIFICATIONS
    # ============================================================================
    
    def _send_requirement_notification(
        self,
        requirement_id: str,
        reminder_type: str = 'initial'
    ) -> None:
        """Send notification to parents about a requirement"""
        # Get requirement details
        req_query = """
        SELECT name, requirement_type, due_date, applies_to, target_class
        FROM school_requirements WHERE id = %s
        """
        requirement = self.db.execute_query(req_query, (requirement_id,), fetch=True)[0]
        
        # Get affected students/parents
        if requirement['applies_to'] == 'all_students':
            students_query = """
            SELECT DISTINCT s.id as student_id, p.id as parent_id
            FROM students s
            JOIN student_parents sp ON sp.student_id = s.id
            JOIN parents p ON p.id = sp.parent_id
            WHERE s.school_id = %s AND s.status = 'active'
            """
            params = [self.school_id]
        else:
            students_query = """
            SELECT DISTINCT s.id as student_id, p.id as parent_id
            FROM students s
            JOIN student_parents sp ON sp.student_id = s.id
            JOIN parents p ON p.id = sp.parent_id
            WHERE s.school_id = %s AND s.class_name = %s AND s.status = 'active'
            """
            params = [self.school_id, requirement['target_class']]
        
        affected = self.db.execute_query(students_query, tuple(params), fetch=True)
        
        # Send notifications (via notification service)
        # TODO: Implement actual notification sending
        
        # Log reminders
        for item in affected:
            self.db.execute_query(
                """
                INSERT INTO requirement_reminders (
                    school_id, requirement_id, student_id, reminder_type
                ) VALUES (%s, %s, %s, %s)
                """,
                (self.school_id, requirement_id, item['student_id'], reminder_type)
            )


def get_requirements_service(school_id: str) -> SchoolRequirementsService:
    """Helper to get requirements service instance"""
    return SchoolRequirementsService(school_id)
