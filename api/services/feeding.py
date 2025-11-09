"""
School Feeding Service
Meal planning, menu management, meal attendance tracking
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date

from api.services.database import get_db_manager


class FeedingService:
    """Service for school feeding program"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # MEAL MENU MANAGEMENT
    # ============================================================================
    
    def create_meal_menu(
        self,
        meal_type: str,  # breakfast, lunch, dinner, snack
        menu_date: str,
        items: List[str],
        description: Optional[str] = None,
        allergen_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create meal menu for a specific date"""
        query = """
        INSERT INTO meal_menu (
            school_id, meal_type, menu_date, items, description, allergen_info
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, meal_type, menu_date, items, description, allergen_info),
            fetch=True
        )
        
        return {
            "success": True,
            "menu_id": result[0]['id'],
            "meal_type": meal_type,
            "menu_date": menu_date
        }
    
    def get_menu_for_date(self, menu_date: str) -> List[Dict[str, Any]]:
        """Get all meals for a specific date"""
        query = """
        SELECT 
            id,
            meal_type,
            items,
            description,
            allergen_info
        FROM meal_menu
        WHERE school_id = %s AND menu_date = %s
        ORDER BY 
            CASE meal_type
                WHEN 'breakfast' THEN 1
                WHEN 'lunch' THEN 2
                WHEN 'snack' THEN 3
                WHEN 'dinner' THEN 4
            END
        """
        
        return self.db.execute_query(query, (self.school_id, menu_date), fetch=True)
    
    def get_weekly_menu(self, start_date: str) -> Dict[str, Any]:
        """Get menu for a week"""
        query = """
        SELECT 
            menu_date,
            meal_type,
            items,
            description
        FROM meal_menu
        WHERE school_id = %s
        AND menu_date BETWEEN %s AND %s::date + INTERVAL '6 days'
        ORDER BY menu_date, meal_type
        """
        
        menus = self.db.execute_query(query, (self.school_id, start_date, start_date), fetch=True)
        
        # Group by date
        weekly_menu = {}
        for menu in menus:
            date_str = menu['menu_date'].strftime('%Y-%m-%d')
            if date_str not in weekly_menu:
                weekly_menu[date_str] = []
            weekly_menu[date_str].append({
                "meal_type": menu['meal_type'],
                "items": menu['items'],
                "description": menu['description']
            })
        
        return {
            "success": True,
            "start_date": start_date,
            "weekly_menu": weekly_menu
        }
    
    # ============================================================================
    # MEAL ATTENDANCE
    # ============================================================================
    
    def record_meal_attendance(
        self,
        student_id: str,
        meal_type: str,
        meal_date: str,
        attended: bool = True
    ) -> Dict[str, Any]:
        """Record student meal attendance"""
        query = """
        INSERT INTO meal_attendance (
            school_id, student_id, meal_type, meal_date, attended
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (student_id, meal_date, meal_type) DO UPDATE
        SET attended = EXCLUDED.attended
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, meal_type, meal_date, attended),
            fetch=True
        )
        
        return {
            "success": True,
            "attendance_id": result[0]['id'],
            "student_id": student_id,
            "meal_type": meal_type,
            "attended": attended
        }
    
    def bulk_record_meal_attendance(
        self,
        meal_type: str,
        meal_date: str,
        student_ids: List[str]
    ) -> Dict[str, Any]:
        """Record meal attendance for multiple students"""
        recorded = []
        
        for student_id in student_ids:
            result = self.record_meal_attendance(
                student_id=student_id,
                meal_type=meal_type,
                meal_date=meal_date,
                attended=True
            )
            recorded.append(result)
        
        return {
            "success": True,
            "meal_type": meal_type,
            "meal_date": meal_date,
            "students_recorded": len(recorded)
        }
    
    def get_meal_attendance_for_date(
        self,
        meal_date: str,
        meal_type: str
    ) -> List[Dict[str, Any]]:
        """Get meal attendance for a specific date and meal"""
        query = """
        SELECT 
            ma.student_id,
            ma.attended,
            s.first_name,
            s.last_name,
            s.class_name
        FROM meal_attendance ma
        JOIN students s ON s.id = ma.student_id
        WHERE ma.school_id = %s
        AND ma.meal_date = %s
        AND ma.meal_type = %s
        ORDER BY s.class_name, s.first_name
        """
        
        return self.db.execute_query(query, (self.school_id, meal_date, meal_type), fetch=True)
    
    def get_student_meal_history(
        self,
        student_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get meal attendance history for a student"""
        query = """
        SELECT 
            meal_date,
            meal_type,
            attended
        FROM meal_attendance
        WHERE student_id = %s
        AND meal_date BETWEEN %s AND %s
        ORDER BY meal_date DESC, meal_type
        """
        
        return self.db.execute_query(query, (student_id, start_date, end_date), fetch=True)
    
    # ============================================================================
    # ANALYTICS
    # ============================================================================
    
    def get_daily_meal_count(self, meal_date: str) -> Dict[str, Any]:
        """Get meal count for a specific date"""
        query = """
        SELECT 
            meal_type,
            COUNT(*) as count
        FROM meal_attendance
        WHERE school_id = %s
        AND meal_date = %s
        AND attended = true
        GROUP BY meal_type
        """
        
        counts = self.db.execute_query(query, (self.school_id, meal_date), fetch=True)
        
        return {
            "success": True,
            "meal_date": meal_date,
            "meal_counts": counts,
            "total_meals_served": sum(c['count'] for c in counts)
        }
    
    def get_feeding_statistics(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get feeding statistics for a period"""
        query = """
        SELECT 
            meal_type,
            COUNT(*) as total_servings,
            COUNT(DISTINCT student_id) as unique_students
        FROM meal_attendance
        WHERE school_id = %s
        AND meal_date BETWEEN %s AND %s
        AND attended = true
        GROUP BY meal_type
        """
        
        stats = self.db.execute_query(query, (self.school_id, start_date, end_date), fetch=True)
        
        return {
            "success": True,
            "period": f"{start_date} to {end_date}",
            "statistics": stats,
            "total_meals_served": sum(s['total_servings'] for s in stats)
        }
    
    def get_students_not_eating(self, days: int = 3) -> List[Dict[str, Any]]:
        """
        Get students who haven't eaten meals in X days
        (Welfare check)
        """
        query = """
        SELECT DISTINCT
            s.id,
            s.first_name,
            s.last_name,
            s.class_name,
            (
                SELECT MAX(meal_date)
                FROM meal_attendance
                WHERE student_id = s.id AND attended = true
            ) as last_meal_date
        FROM students s
        WHERE s.school_id = %s
        AND s.status = 'active'
        AND NOT EXISTS (
            SELECT 1
            FROM meal_attendance ma
            WHERE ma.student_id = s.id
            AND ma.meal_date >= CURRENT_DATE - %s
            AND ma.attended = true
        )
        ORDER BY s.class_name, s.first_name
        """
        
        return self.db.execute_query(query, (self.school_id, days), fetch=True)


def get_feeding_service(school_id: str) -> FeedingService:
    """Helper to get feeding service instance"""
    return FeedingService(school_id)
