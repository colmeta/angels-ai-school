"""
School Transport Service
Bus routes, schedules, driver info, student assignments (NO GPS TRACKING)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, time

from api.services.database import get_db_manager


class TransportService:
    """Service for school transport management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # TRANSPORT ROUTES
    # ============================================================================
    
    def create_route(
        self,
        route_name: str,
        route_code: str,
        driver_name: str,
        driver_phone: str,
        vehicle_number: str,
        vehicle_capacity: int,
        pickup_time: str,
        dropoff_time: str,
        stops: List[Dict]  # [{name: "Stop 1", arrival_time: "07:00"}]
    ) -> Dict[str, Any]:
        """
        Create transport route
        
        Example stops: [
            {"name": "Ntinda", "arrival_time": "06:30"},
            {"name": "Bukoto", "arrival_time": "06:45"},
            {"name": "Kamwokya", "arrival_time": "07:00"}
        ]
        """
        query = """
        INSERT INTO transport_routes (
            school_id, route_name, route_code, driver_name, driver_phone,
            vehicle_number, vehicle_capacity, pickup_time, dropoff_time, stops
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, route_name, route_code, driver_name, driver_phone,
             vehicle_number, vehicle_capacity, pickup_time, dropoff_time, stops),
            fetch=True
        )
        
        return {
            "success": True,
            "route_id": result[0]['id'],
            "route_name": route_name,
            "route_code": route_code,
            "driver": driver_name,
            "vehicle": vehicle_number
        }
    
    def get_routes(self, is_active: bool = True) -> List[Dict[str, Any]]:
        """Get all transport routes"""
        query = """
        SELECT 
            id,
            route_name,
            route_code,
            driver_name,
            driver_phone,
            vehicle_number,
            vehicle_capacity,
            pickup_time,
            dropoff_time,
            stops,
            is_active
        FROM transport_routes
        WHERE school_id = %s AND is_active = %s
        ORDER BY route_name
        """
        
        return self.db.execute_query(query, (self.school_id, is_active), fetch=True)
    
    def update_route(self, route_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update route details"""
        allowed_fields = [
            'route_name', 'driver_name', 'driver_phone', 'vehicle_number',
            'vehicle_capacity', 'pickup_time', 'dropoff_time', 'stops'
        ]
        
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = %s")
                values.append(value)
        
        if not set_clauses:
            return {"success": False, "error": "No valid fields to update"}
        
        query = f"""
        UPDATE transport_routes
        SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND school_id = %s
        """
        
        values.extend([route_id, self.school_id])
        self.db.execute_query(query, tuple(values))
        
        return {"success": True, "route_id": route_id}
    
    # ============================================================================
    # STUDENT ASSIGNMENTS
    # ============================================================================
    
    def assign_student_to_route(
        self,
        student_id: str,
        route_id: str,
        stop_name: str,
        monthly_fee: float
    ) -> Dict[str, Any]:
        """Assign student to transport route"""
        query = """
        INSERT INTO student_transport (
            school_id, student_id, route_id, stop_name, monthly_fee
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (student_id) DO UPDATE
        SET route_id = EXCLUDED.route_id,
            stop_name = EXCLUDED.stop_name,
            monthly_fee = EXCLUDED.monthly_fee
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, route_id, stop_name, monthly_fee),
            fetch=True
        )
        
        return {
            "success": True,
            "assignment_id": result[0]['id'],
            "student_id": student_id,
            "route_id": route_id
        }
    
    def get_students_on_route(self, route_id: str) -> List[Dict[str, Any]]:
        """Get all students assigned to a route"""
        query = """
        SELECT 
            st.id as assignment_id,
            st.student_id,
            st.stop_name,
            st.monthly_fee,
            st.is_active,
            s.first_name,
            s.last_name,
            s.class_name,
            p.phone as parent_phone
        FROM student_transport st
        JOIN students s ON s.id = st.student_id
        LEFT JOIN student_parents sp ON sp.student_id = s.id
        LEFT JOIN parents p ON p.id = sp.parent_id
        WHERE st.route_id = %s AND st.is_active = true
        ORDER BY st.stop_name, s.first_name
        """
        
        return self.db.execute_query(query, (route_id,), fetch=True)
    
    def get_student_transport_info(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get transport info for a student"""
        query = """
        SELECT 
            st.id,
            st.stop_name,
            st.monthly_fee,
            tr.route_name,
            tr.route_code,
            tr.driver_name,
            tr.driver_phone,
            tr.vehicle_number,
            tr.pickup_time,
            tr.dropoff_time,
            tr.stops
        FROM student_transport st
        JOIN transport_routes tr ON tr.id = st.route_id
        WHERE st.student_id = %s AND st.is_active = true
        """
        
        result = self.db.execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None
    
    def remove_student_from_transport(self, student_id: str) -> Dict[str, Any]:
        """Remove student from transport"""
        query = """
        UPDATE student_transport
        SET is_active = false, updated_at = CURRENT_TIMESTAMP
        WHERE student_id = %s
        """
        
        self.db.execute_query(query, (student_id,))
        
        return {"success": True, "student_id": student_id}
    
    # ============================================================================
    # SCHEDULES & NOTIFICATIONS
    # ============================================================================
    
    def get_daily_schedule(self, date: str) -> List[Dict[str, Any]]:
        """Get all active routes for a specific date"""
        query = """
        SELECT 
            tr.id as route_id,
            tr.route_name,
            tr.route_code,
            tr.driver_name,
            tr.driver_phone,
            tr.vehicle_number,
            tr.pickup_time,
            tr.dropoff_time,
            COUNT(st.id) as student_count
        FROM transport_routes tr
        LEFT JOIN student_transport st ON st.route_id = tr.id AND st.is_active = true
        WHERE tr.school_id = %s AND tr.is_active = true
        GROUP BY tr.id, tr.route_name, tr.route_code, tr.driver_name, 
                 tr.driver_phone, tr.vehicle_number, tr.pickup_time, tr.dropoff_time
        ORDER BY tr.pickup_time
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    def bulk_notify_parents(self, route_id: str, message: str) -> Dict[str, Any]:
        """
        Send notification to all parents on a route
        (e.g., "Bus delayed by 15 minutes")
        """
        students = self.get_students_on_route(route_id)
        
        notifications_sent = []
        
        for student in students:
            if student.get('parent_phone'):
                # Here you would integrate with NotificationService
                notifications_sent.append({
                    "student_id": student['student_id'],
                    "parent_phone": student['parent_phone'],
                    "message": message
                })
        
        return {
            "success": True,
            "route_id": route_id,
            "notifications_sent": len(notifications_sent),
            "recipients": notifications_sent
        }
    
    # ============================================================================
    # ANALYTICS
    # ============================================================================
    
    def get_route_capacity_report(self) -> List[Dict[str, Any]]:
        """Get capacity utilization for all routes"""
        query = """
        SELECT 
            tr.route_name,
            tr.vehicle_capacity,
            COUNT(st.id) as students_assigned,
            tr.vehicle_capacity - COUNT(st.id) as available_seats,
            ROUND((COUNT(st.id)::DECIMAL / tr.vehicle_capacity) * 100, 1) as utilization_percentage
        FROM transport_routes tr
        LEFT JOIN student_transport st ON st.route_id = tr.id AND st.is_active = true
        WHERE tr.school_id = %s AND tr.is_active = true
        GROUP BY tr.id, tr.route_name, tr.vehicle_capacity
        ORDER BY utilization_percentage DESC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    def get_monthly_transport_revenue(self, month: str) -> Dict[str, Any]:
        """Calculate expected transport revenue for a month"""
        query = """
        SELECT 
            COUNT(st.id) as total_students,
            SUM(st.monthly_fee) as total_monthly_revenue
        FROM student_transport st
        WHERE st.school_id = %s AND st.is_active = true
        """
        
        result = self.db.execute_query(query, (self.school_id,), fetch=True)
        
        return {
            "success": True,
            "month": month,
            "total_students": result[0]['total_students'] if result else 0,
            "total_revenue": float(result[0]['total_monthly_revenue'] or 0) if result else 0
        }


def get_transport_service(school_id: str) -> TransportService:
    """Helper to get transport service instance"""
    return TransportService(school_id)
