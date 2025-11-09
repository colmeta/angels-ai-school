"""
Boarding School Service
Dormitories, bed assignments, boarding items tracking, exeat requests
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.services.database import get_db_manager


class BoardingService:
    """Service for boarding school operations"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # DORMITORY MANAGEMENT
    # ============================================================================
    
    def create_dormitory(
        self,
        name: str,
        dormitory_type: str,  # boys, girls, mixed
        capacity: int,
        matron_name: Optional[str] = None,
        matron_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a dormitory"""
        query = """
        INSERT INTO dormitories (
            school_id, name, dormitory_type, capacity, matron_name, matron_phone
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, name, dormitory_type, capacity, matron_name, matron_phone),
            fetch=True
        )
        
        return {
            "success": True,
            "dormitory_id": result[0]['id'],
            "name": name,
            "capacity": capacity
        }
    
    def get_dormitories(self) -> List[Dict[str, Any]]:
        """Get all dormitories"""
        query = """
        SELECT 
            d.id,
            d.name,
            d.dormitory_type,
            d.capacity,
            d.matron_name,
            d.matron_phone,
            COUNT(db.id) as occupied_beds,
            d.capacity - COUNT(db.id) as available_beds
        FROM dormitories d
        LEFT JOIN dormitory_beds db ON db.dormitory_id = d.id AND db.is_occupied = true
        WHERE d.school_id = %s
        GROUP BY d.id, d.name, d.dormitory_type, d.capacity, d.matron_name, d.matron_phone
        ORDER BY d.name
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    def create_beds(
        self,
        dormitory_id: str,
        bed_count: int,
        bed_prefix: str = "BED"
    ) -> Dict[str, Any]:
        """Create multiple beds in a dormitory"""
        beds_created = []
        
        for i in range(1, bed_count + 1):
            bed_number = f"{bed_prefix}-{i:03d}"
            
            query = """
            INSERT INTO dormitory_beds (school_id, dormitory_id, bed_number)
            VALUES (%s, %s, %s)
            RETURNING id
            """
            
            result = self.db.execute_query(
                query,
                (self.school_id, dormitory_id, bed_number),
                fetch=True
            )
            
            beds_created.append({
                "bed_id": result[0]['id'],
                "bed_number": bed_number
            })
        
        return {
            "success": True,
            "dormitory_id": dormitory_id,
            "beds_created": len(beds_created),
            "beds": beds_created
        }
    
    # ============================================================================
    # BED ASSIGNMENTS
    # ============================================================================
    
    def assign_bed(
        self,
        student_id: str,
        bed_id: str
    ) -> Dict[str, Any]:
        """Assign student to a bed"""
        # Check if bed is available
        check_query = """
        SELECT is_occupied FROM dormitory_beds WHERE id = %s
        """
        bed = self.db.execute_query(check_query, (bed_id,), fetch=True)
        
        if not bed:
            return {"success": False, "error": "Bed not found"}
        
        if bed[0]['is_occupied']:
            return {"success": False, "error": "Bed is already occupied"}
        
        # Assign bed
        update_query = """
        UPDATE dormitory_beds
        SET student_id = %s,
            is_occupied = true,
            assigned_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        self.db.execute_query(update_query, (student_id, bed_id))
        
        return {
            "success": True,
            "student_id": student_id,
            "bed_id": bed_id
        }
    
    def get_student_bed(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get bed assignment for a student"""
        query = """
        SELECT 
            db.id as bed_id,
            db.bed_number,
            d.name as dormitory_name,
            d.matron_name,
            d.matron_phone
        FROM dormitory_beds db
        JOIN dormitories d ON d.id = db.dormitory_id
        WHERE db.student_id = %s AND db.is_occupied = true
        """
        
        result = self.db.execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None
    
    def vacate_bed(self, bed_id: str) -> Dict[str, Any]:
        """Vacate a bed"""
        query = """
        UPDATE dormitory_beds
        SET student_id = NULL,
            is_occupied = false,
            assigned_at = NULL
        WHERE id = %s
        """
        
        self.db.execute_query(query, (bed_id,))
        
        return {"success": True, "bed_id": bed_id}
    
    # ============================================================================
    # BOARDING ITEMS TRACKING
    # ============================================================================
    
    def track_boarding_items(
        self,
        student_id: str,
        items: List[Dict[str, Any]]  # [{name: "Mattress", quantity: 1, condition: "new"}]
    ) -> Dict[str, Any]:
        """
        Track boarding items brought by student
        (mattress, bedsheets, blankets, plates, cups, etc.)
        """
        items_tracked = []
        
        for item in items:
            query = """
            INSERT INTO boarding_items (
                school_id, student_id, item_name, quantity, condition, brought_at
            ) VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
            """
            
            result = self.db.execute_query(
                query,
                (self.school_id, student_id, item['name'], 
                 item.get('quantity', 1), item.get('condition', 'good')),
                fetch=True
            )
            
            items_tracked.append({
                "item_id": result[0]['id'],
                "item_name": item['name']
            })
        
        return {
            "success": True,
            "student_id": student_id,
            "items_tracked": len(items_tracked),
            "items": items_tracked
        }
    
    def get_student_boarding_items(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all boarding items for a student"""
        query = """
        SELECT 
            id,
            item_name,
            quantity,
            condition,
            brought_at,
            returned_at
        FROM boarding_items
        WHERE student_id = %s
        ORDER BY brought_at DESC
        """
        
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    def return_boarding_item(
        self,
        item_id: str,
        return_condition: str
    ) -> Dict[str, Any]:
        """Mark boarding item as returned"""
        query = """
        UPDATE boarding_items
        SET returned_at = CURRENT_TIMESTAMP,
            condition = %s
        WHERE id = %s
        """
        
        self.db.execute_query(query, (return_condition, item_id))
        
        return {
            "success": True,
            "item_id": item_id,
            "return_condition": return_condition
        }
    
    # ============================================================================
    # EXEAT REQUESTS (Permission to leave school)
    # ============================================================================
    
    def create_exeat_request(
        self,
        student_id: str,
        parent_id: str,
        reason: str,
        leave_date: str,
        return_date: str
    ) -> Dict[str, Any]:
        """Create exeat request (permission to leave boarding)"""
        query = """
        INSERT INTO exeat_requests (
            school_id, student_id, parent_id, reason, leave_date, return_date
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, parent_id, reason, leave_date, return_date),
            fetch=True
        )
        
        return {
            "success": True,
            "exeat_id": result[0]['id'],
            "student_id": student_id,
            "status": "pending"
        }
    
    def approve_exeat(
        self,
        exeat_id: str,
        approved_by: str
    ) -> Dict[str, Any]:
        """Approve exeat request"""
        query = """
        UPDATE exeat_requests
        SET status = 'approved',
            approved_by = %s,
            approved_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        self.db.execute_query(query, (approved_by, exeat_id))
        
        return {
            "success": True,
            "exeat_id": exeat_id,
            "status": "approved"
        }
    
    def record_student_departure(
        self,
        exeat_id: str
    ) -> Dict[str, Any]:
        """Record when student actually leaves"""
        query = """
        UPDATE exeat_requests
        SET actual_departure = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        self.db.execute_query(query, (exeat_id,))
        
        return {
            "success": True,
            "exeat_id": exeat_id
        }
    
    def record_student_return(
        self,
        exeat_id: str
    ) -> Dict[str, Any]:
        """Record when student returns"""
        query = """
        UPDATE exeat_requests
        SET actual_return = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        self.db.execute_query(query, (exeat_id,))
        
        return {
            "success": True,
            "exeat_id": exeat_id
        }
    
    def get_pending_exeats(self) -> List[Dict[str, Any]]:
        """Get all pending exeat requests"""
        query = """
        SELECT 
            e.id,
            e.student_id,
            e.reason,
            e.leave_date,
            e.return_date,
            s.first_name,
            s.last_name,
            p.first_name as parent_first_name,
            p.last_name as parent_last_name
        FROM exeat_requests e
        JOIN students s ON s.id = e.student_id
        JOIN parents p ON p.id = e.parent_id
        WHERE e.school_id = %s AND e.status = 'pending'
        ORDER BY e.created_at DESC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    def get_students_currently_away(self) -> List[Dict[str, Any]]:
        """Get all students currently on exeat"""
        query = """
        SELECT 
            e.id as exeat_id,
            e.student_id,
            e.leave_date,
            e.return_date,
            s.first_name,
            s.last_name,
            d.name as dormitory_name
        FROM exeat_requests e
        JOIN students s ON s.id = e.student_id
        LEFT JOIN dormitory_beds db ON db.student_id = s.id
        LEFT JOIN dormitories d ON d.id = db.dormitory_id
        WHERE e.school_id = %s
        AND e.status = 'approved'
        AND e.actual_departure IS NOT NULL
        AND e.actual_return IS NULL
        ORDER BY e.return_date ASC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)


def get_boarding_service(school_id: str) -> BoardingService:
    """Helper to get boarding service instance"""
    return BoardingService(school_id)
