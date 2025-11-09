"""
Multi-Role Service
Handles users with multiple roles (e.g., teacher + parent) at same or different schools
Provides role switching and appropriate dashboard data
"""
from typing import Dict, Any, List, Optional

from api.services.database import get_db_manager


class MultiRoleService:
    """Service for managing multi-role users"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = get_db_manager()
    
    # ============================================================================
    # ROLE DETECTION & MANAGEMENT
    # ============================================================================
    
    def get_roles_at_school(self, school_id: str) -> List[str]:
        """
        Get all roles a user has at a specific school
        
        Example: Mr. Mukasa at Angels Primary
        Returns: ['teacher', 'parent']
        """
        query = """
        SELECT DISTINCT role
        FROM user_school_access
        WHERE user_id = %s AND school_id = %s AND is_active = true
        ORDER BY role
        """
        
        roles = self.db.execute_query(query, (self.user_id, school_id), fetch=True)
        return [r['role'] for r in roles]
    
    def get_all_roles_across_schools(self) -> Dict[str, List[str]]:
        """
        Get all roles across all schools
        
        Example: Mr. Mukasa
        Returns: {
            'school-a': ['teacher', 'parent'],
            'school-b': ['parent']
        }
        """
        query = """
        SELECT school_id, role
        FROM user_school_access
        WHERE user_id = %s AND is_active = true
        ORDER BY school_id, role
        """
        
        rows = self.db.execute_query(query, (self.user_id,), fetch=True)
        
        roles_by_school = {}
        for row in rows:
            school_id = row['school_id']
            if school_id not in roles_by_school:
                roles_by_school[school_id] = []
            roles_by_school[school_id].append(row['role'])
        
        return roles_by_school
    
    def has_multiple_roles_at_school(self, school_id: str) -> bool:
        """Check if user has multiple roles at a specific school"""
        roles = self.get_roles_at_school(school_id)
        return len(roles) > 1
    
    def get_entity_ids_for_role(self, school_id: str, role: str) -> List[str]:
        """
        Get entity IDs for a specific role
        
        Example: Get teacher_id if role='teacher', parent_id if role='parent'
        """
        query = """
        SELECT ul.entity_id
        FROM user_links ul
        WHERE ul.user_id = %s AND ul.entity_type = %s
        """
        
        rows = self.db.execute_query(query, (self.user_id, role), fetch=True)
        return [r['entity_id'] for r in rows]
    
    # ============================================================================
    # ROLE PREFERENCES
    # ============================================================================
    
    def get_preferred_role(self, school_id: str) -> str:
        """Get user's preferred role at a school (or most recently used)"""
        query = """
        SELECT preferred_role, last_used_role
        FROM user_role_preferences
        WHERE user_id = %s AND school_id = %s
        """
        
        prefs = self.db.execute_query(query, (self.user_id, school_id), fetch=True)
        
        if prefs:
            return prefs[0]['last_used_role'] or prefs[0]['preferred_role']
        
        # Default to first role if no preference set
        roles = self.get_roles_at_school(school_id)
        return roles[0] if roles else None
    
    def set_preferred_role(self, school_id: str, role: str) -> Dict[str, Any]:
        """Set user's preferred role at a school"""
        query = """
        INSERT INTO user_role_preferences (user_id, school_id, preferred_role, last_used_role)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, school_id)
        DO UPDATE SET
            preferred_role = EXCLUDED.preferred_role,
            last_used_role = EXCLUDED.last_used_role,
            role_switch_count = user_role_preferences.role_switch_count + 1,
            updated_at = CURRENT_TIMESTAMP
        """
        
        self.db.execute_query(query, (self.user_id, school_id, role, role))
        
        return {
            "success": True,
            "user_id": self.user_id,
            "school_id": school_id,
            "preferred_role": role
        }
    
    def switch_role(self, school_id: str, new_role: str) -> Dict[str, Any]:
        """
        Switch to a different role at the same school
        
        Example: Mr. Mukasa switches from Teacher Mode to Parent Mode
        """
        # Verify user has this role
        roles = self.get_roles_at_school(school_id)
        
        if new_role not in roles:
            return {
                "success": False,
                "error": f"User does not have role '{new_role}' at this school"
            }
        
        # Update preference
        self.set_preferred_role(school_id, new_role)
        
        return {
            "success": True,
            "new_role": new_role,
            "school_id": school_id
        }
    
    # ============================================================================
    # DASHBOARD DATA
    # ============================================================================
    
    def get_dashboard_for_role(self, school_id: str, role: str) -> Dict[str, Any]:
        """
        Get appropriate dashboard data based on role
        
        - teacher: Classes, students, timetable
        - parent: Children, fees, notifications
        - admin: School stats, users, settings
        """
        if role == 'teacher':
            return self._get_teacher_dashboard(school_id)
        elif role == 'parent':
            return self._get_parent_dashboard(school_id)
        elif role == 'admin':
            return self._get_admin_dashboard(school_id)
        elif role == 'staff':
            return self._get_staff_dashboard(school_id)
        else:
            return {"error": "Unknown role"}
    
    def _get_teacher_dashboard(self, school_id: str) -> Dict[str, Any]:
        """Get teacher-specific dashboard data"""
        # Get teacher entity IDs
        teacher_ids = self.get_entity_ids_for_role(school_id, 'teacher')
        
        if not teacher_ids:
            return {"error": "No teacher entity found"}
        
        teacher_id = teacher_ids[0]
        
        # Get teacher's classes
        classes_query = """
        SELECT DISTINCT class_name, subject
        FROM teachers
        WHERE id = %s
        """
        classes = self.db.execute_query(classes_query, (teacher_id,), fetch=True)
        
        # Get student count per class
        # Get today's attendance summary
        # Get recent activities
        
        return {
            "role": "teacher",
            "teacher_id": teacher_id,
            "classes": classes,
            "dashboard_type": "teacher"
        }
    
    def _get_parent_dashboard(self, school_id: str) -> Dict[str, Any]:
        """Get parent-specific dashboard data"""
        # Get children
        children_query = """
        SELECT 
            s.id, s.first_name, s.last_name, s.class_name, s.admission_number
        FROM parent_children_global pcg
        JOIN students s ON s.id = pcg.child_student_id
        WHERE pcg.parent_user_id = %s AND pcg.school_id = %s
        ORDER BY s.first_name
        """
        
        children = self.db.execute_query(children_query, (self.user_id, school_id), fetch=True)
        
        # For each child, get summary data
        children_data = []
        for child in children:
            # Get today's attendance
            attendance_query = """
            SELECT status FROM attendance
            WHERE student_id = %s AND date = CURRENT_DATE
            LIMIT 1
            """
            attendance = self.db.execute_query(attendance_query, (child['id'],), fetch=True)
            
            # Get fee balance
            fee_query = """
            SELECT SUM(balance) as balance FROM student_fees
            WHERE student_id = %s
            """
            fees = self.db.execute_query(fee_query, (child['id'],), fetch=True)
            
            children_data.append({
                **child,
                "attendance_today": attendance[0]['status'] if attendance else 'unknown',
                "fee_balance": float(fees[0]['balance']) if fees and fees[0]['balance'] else 0
            })
        
        return {
            "role": "parent",
            "children": children_data,
            "dashboard_type": "parent"
        }
    
    def _get_admin_dashboard(self, school_id: str) -> Dict[str, Any]:
        """Get admin-specific dashboard data"""
        # School stats
        stats_query = """
        SELECT 
            (SELECT COUNT(*) FROM students WHERE school_id = %s AND status = 'active') as total_students,
            (SELECT COUNT(*) FROM teachers WHERE school_id = %s) as total_teachers,
            (SELECT COUNT(*) FROM parents WHERE school_id = %s) as total_parents
        """
        stats = self.db.execute_query(stats_query, (school_id, school_id, school_id), fetch=True)[0]
        
        return {
            "role": "admin",
            "stats": stats,
            "dashboard_type": "admin"
        }
    
    def _get_staff_dashboard(self, school_id: str) -> Dict[str, Any]:
        """Get staff-specific dashboard data"""
        return {
            "role": "staff",
            "dashboard_type": "staff"
        }
    
    # ============================================================================
    # MULTI-ROLE USER SUMMARY
    # ============================================================================
    
    def get_user_summary(self) -> Dict[str, Any]:
        """
        Get complete summary of user's roles and schools
        
        Perfect for initial login to show all user's roles
        """
        query = """
        SELECT * FROM user_roles_at_school
        WHERE user_id = %s
        """
        
        schools = self.db.execute_query(query, (self.user_id,), fetch=True)
        
        return {
            "user_id": self.user_id,
            "total_schools": len(schools),
            "schools": schools,
            "has_multiple_roles": any(s['role_count'] > 1 for s in schools)
        }


def get_multi_role_service(user_id: str) -> MultiRoleService:
    """Helper to get multi-role service instance"""
    return MultiRoleService(user_id)
