"""
Multi-School Service
Handles cross-school access for parents with children in different schools
Enables single login, school switching, and combined views
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from api.services.database import get_db_manager
from api.services.notifications import NotificationService


class MultiSchoolService:
    """Service for managing multi-school access"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = get_db_manager()
        self.notification_service = NotificationService()
    
    # ============================================================================
    # USER SCHOOLS MANAGEMENT
    # ============================================================================
    
    def get_user_schools(self) -> Dict[str, Any]:
        """
        Get all schools a user has access to
        
        Returns:
            List of schools with role, children, and access info
        """
        query = """
        SELECT 
            usa.school_id,
            s.name as school_name,
            s.code as school_code,
            s.country,
            s.region,
            usa.role,
            usa.is_active,
            usa.last_accessed,
            sb.brand_name,
            sb.primary_color
        FROM user_school_access usa
        JOIN schools s ON s.id = usa.school_id
        LEFT JOIN school_branding sb ON sb.school_id = s.id
        WHERE usa.user_id = %s AND usa.is_active = true
        ORDER BY usa.last_accessed DESC NULLS LAST, s.name
        """
        
        schools = self.db.execute_query(query, (self.user_id,), fetch=True)
        
        # For each school, get children if user is a parent
        result = []
        for school in schools:
            school_data = dict(school)
            
            if school['role'] == 'parent':
                # Get children at this school
                children_query = """
                SELECT 
                    s.id, s.first_name, s.last_name, s.class_name, 
                    s.admission_number, s.photo_url,
                    pcg.relationship, pcg.is_primary
                FROM parent_children_global pcg
                JOIN students s ON s.id = pcg.child_student_id
                WHERE pcg.parent_user_id = %s AND pcg.school_id = %s
                ORDER BY s.first_name
                """
                children = self.db.execute_query(
                    children_query, 
                    (self.user_id, school['school_id']), 
                    fetch=True
                )
                school_data['children'] = children
                school_data['children_count'] = len(children)
            else:
                school_data['children'] = []
                school_data['children_count'] = 0
            
            result.append(school_data)
        
        return {
            "user_id": self.user_id,
            "total_schools": len(result),
            "schools": result
        }
    
    def get_combined_dashboard(self) -> Dict[str, Any]:
        """
        Get combined dashboard for all schools
        Shows all children across all schools in one view
        """
        schools_data = self.get_user_schools()
        
        combined_data = {
            "user_id": self.user_id,
            "total_schools": schools_data['total_schools'],
            "schools": []
        }
        
        total_fees = 0
        total_notifications = 0
        
        for school in schools_data['schools']:
            school_summary = {
                "school_id": school['school_id'],
                "school_name": school['school_name'],
                "brand_name": school['brand_name'],
                "children": []
            }
            
            if school['role'] == 'parent':
                # Get detailed info for each child
                for child in school['children']:
                    child_data = self._get_child_summary(
                        child['id'], 
                        school['school_id']
                    )
                    school_summary['children'].append(child_data)
                    
                    # Add to totals
                    if 'fee_balance' in child_data:
                        total_fees += child_data['fee_balance']
            
            # Get recent notifications for this school
            notifications = self._get_school_notifications(school['school_id'])
            school_summary['recent_notifications'] = notifications
            total_notifications += len(notifications)
            
            combined_data['schools'].append(school_summary)
        
        combined_data['total_fee_balance'] = total_fees
        combined_data['total_unread_notifications'] = total_notifications
        
        return combined_data
    
    def _get_child_summary(self, student_id: str, school_id: str) -> Dict[str, Any]:
        """Get summary data for a child"""
        # Student basic info
        student_query = """
        SELECT id, first_name, last_name, class_name, admission_number, photo_url
        FROM students WHERE id = %s
        """
        student = self.db.execute_query(student_query, (student_id,), fetch=True)[0]
        
        # Today's attendance
        attendance_query = """
        SELECT status FROM attendance
        WHERE student_id = %s AND date = CURRENT_DATE
        LIMIT 1
        """
        attendance = self.db.execute_query(attendance_query, (student_id,), fetch=True)
        attendance_today = attendance[0]['status'] if attendance else 'unknown'
        
        # Fee balance
        fee_query = """
        SELECT SUM(balance) as balance
        FROM student_fees
        WHERE student_id = %s
        """
        fees = self.db.execute_query(fee_query, (student_id,), fetch=True)
        fee_balance = float(fees[0]['balance']) if fees and fees[0]['balance'] else 0
        
        # Recent grade
        grade_query = """
        SELECT a.subject, ar.marks_obtained, a.max_marks, ar.grade
        FROM assessment_results ar
        JOIN assessments a ON a.id = ar.assessment_id
        WHERE ar.student_id = %s
        ORDER BY a.date DESC
        LIMIT 1
        """
        recent_grade = self.db.execute_query(grade_query, (student_id,), fetch=True)
        
        return {
            "id": student['id'],
            "first_name": student['first_name'],
            "last_name": student['last_name'],
            "class_name": student['class_name'],
            "admission_number": student['admission_number'],
            "photo_url": student['photo_url'],
            "attendance_today": attendance_today,
            "fee_balance": fee_balance,
            "recent_grade": recent_grade[0] if recent_grade else None
        }
    
    def _get_school_notifications(self, school_id: str, limit: int = 5) -> List[Dict]:
        """Get recent notifications for a school"""
        query = """
        SELECT id, notification_type, title, message, priority, is_read, created_at
        FROM notifications
        WHERE school_id = %s 
        AND recipient_type = 'parent'
        AND created_at >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        notifications = self.db.execute_query(query, (school_id, limit), fetch=True)
        return notifications
    
    def switch_school(self, school_id: str) -> Dict[str, Any]:
        """
        Switch user's active school and update last accessed
        
        Args:
            school_id: School to switch to
        
        Returns:
            Success status and school info
        """
        # Verify user has access to this school
        verify_query = """
        SELECT school_id, role FROM user_school_access
        WHERE user_id = %s AND school_id = %s AND is_active = true
        """
        access = self.db.execute_query(verify_query, (self.user_id, school_id), fetch=True)
        
        if not access:
            return {
                "success": False,
                "error": "Access denied to this school"
            }
        
        # Update last accessed
        self.db.execute_query(
            """
            UPDATE user_school_access
            SET last_accessed = CURRENT_TIMESTAMP
            WHERE user_id = %s AND school_id = %s
            """,
            (self.user_id, school_id)
        )
        
        # Update user preferences (default school)
        self.db.execute_query(
            """
            INSERT INTO user_preferences (user_id, default_school_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET default_school_id = EXCLUDED.default_school_id,
                updated_at = CURRENT_TIMESTAMP
            """,
            (self.user_id, school_id)
        )
        
        return {
            "success": True,
            "school_id": school_id,
            "role": access[0]['role']
        }
    
    def link_school(self, school_id: str, role: str, access_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Link user to a new school
        
        Args:
            school_id: School to link to
            role: User's role at this school
            access_code: Optional access code for verification
        
        Returns:
            Success status
        """
        # Verify school exists
        school_query = "SELECT id, name FROM schools WHERE id = %s AND is_active = true"
        school = self.db.execute_query(school_query, (school_id,), fetch=True)
        
        if not school:
            return {
                "success": False,
                "error": "School not found"
            }
        
        # TODO: Verify access code if provided
        # This would check against school-specific access codes
        
        # Create access
        try:
            self.db.execute_query(
                """
                INSERT INTO user_school_access (user_id, school_id, role, is_active)
                VALUES (%s, %s, %s, true)
                ON CONFLICT (user_id, school_id, role) 
                DO UPDATE SET is_active = true, updated_at = CURRENT_TIMESTAMP
                """,
                (self.user_id, school_id, role)
            )
            
            return {
                "success": True,
                "school_id": school_id,
                "school_name": school[0]['name'],
                "role": role
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def unlink_school(self, school_id: str) -> Dict[str, Any]:
        """
        Remove user's access to a school
        
        Args:
            school_id: School to unlink
        
        Returns:
            Success status
        """
        self.db.execute_query(
            """
            UPDATE user_school_access
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND school_id = %s
            """,
            (self.user_id, school_id)
        )
        
        return {
            "success": True,
            "school_id": school_id
        }
    
    # ============================================================================
    # PARENT-CHILD MANAGEMENT (CROSS-SCHOOL)
    # ============================================================================
    
    def link_child(
        self, 
        child_student_id: str, 
        school_id: str,
        relationship: str = 'parent',
        is_primary: bool = False
    ) -> Dict[str, Any]:
        """
        Link a child to parent across schools
        
        Args:
            child_student_id: Student ID
            school_id: School ID where child is enrolled
            relationship: father, mother, guardian, sponsor
            is_primary: Is this the primary guardian?
        
        Returns:
            Success status
        """
        # Verify student exists
        student_query = """
        SELECT id, first_name, last_name, class_name
        FROM students WHERE id = %s AND school_id = %s
        """
        student = self.db.execute_query(
            student_query, 
            (child_student_id, school_id), 
            fetch=True
        )
        
        if not student:
            return {
                "success": False,
                "error": "Student not found"
            }
        
        # Link child to parent globally
        try:
            self.db.execute_query(
                """
                INSERT INTO parent_children_global (
                    parent_user_id, child_student_id, school_id,
                    relationship, is_primary
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (parent_user_id, child_student_id)
                DO UPDATE SET 
                    relationship = EXCLUDED.relationship,
                    is_primary = EXCLUDED.is_primary,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (self.user_id, child_student_id, school_id, relationship, is_primary)
            )
            
            # Ensure user has access to this school as parent
            self.link_school(school_id, 'parent')
            
            return {
                "success": True,
                "child_id": child_student_id,
                "child_name": f"{student[0]['first_name']} {student[0]['last_name']}",
                "school_id": school_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_all_children(self) -> List[Dict[str, Any]]:
        """
        Get all children across all schools for this parent
        
        Returns:
            List of all children with school info
        """
        query = """
        SELECT 
            s.id as student_id,
            s.first_name,
            s.last_name,
            s.class_name,
            s.admission_number,
            s.photo_url,
            sch.id as school_id,
            sch.name as school_name,
            pcg.relationship,
            pcg.is_primary
        FROM parent_children_global pcg
        JOIN students s ON s.id = pcg.child_student_id
        JOIN schools sch ON sch.id = pcg.school_id
        WHERE pcg.parent_user_id = %s
        ORDER BY sch.name, s.first_name
        """
        
        children = self.db.execute_query(query, (self.user_id,), fetch=True)
        
        # Group by school
        schools_dict = {}
        for child in children:
            school_id = child['school_id']
            if school_id not in schools_dict:
                schools_dict[school_id] = {
                    "school_id": school_id,
                    "school_name": child['school_name'],
                    "children": []
                }
            
            schools_dict[school_id]['children'].append({
                "student_id": child['student_id'],
                "first_name": child['first_name'],
                "last_name": child['last_name'],
                "class_name": child['class_name'],
                "admission_number": child['admission_number'],
                "photo_url": child['photo_url'],
                "relationship": child['relationship'],
                "is_primary": child['is_primary']
            })
        
        return list(schools_dict.values())


def get_multi_school_service(user_id: str) -> MultiSchoolService:
    """Helper to get multi-school service instance"""
    return MultiSchoolService(user_id)
