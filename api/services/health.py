"""
Health Records & Vaccination Service
Student health records, vaccinations, sick bay visits, medical conditions
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.services.database import get_db_manager


class HealthService:
    """Service for student health management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # HEALTH RECORDS
    # ============================================================================
    
    def create_health_record(
        self,
        student_id: str,
        blood_type: Optional[str] = None,
        allergies: Optional[str] = None,
        chronic_conditions: Optional[str] = None,
        emergency_contact_name: Optional[str] = None,
        emergency_contact_phone: Optional[str] = None,
        medical_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create/update health record for a student"""
        query = """
        INSERT INTO student_health_records (
            school_id, student_id, blood_type, allergies, chronic_conditions,
            emergency_contact_name, emergency_contact_phone, medical_notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (student_id) DO UPDATE
        SET blood_type = EXCLUDED.blood_type,
            allergies = EXCLUDED.allergies,
            chronic_conditions = EXCLUDED.chronic_conditions,
            emergency_contact_name = EXCLUDED.emergency_contact_name,
            emergency_contact_phone = EXCLUDED.emergency_contact_phone,
            medical_notes = EXCLUDED.medical_notes,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, blood_type, allergies, chronic_conditions,
             emergency_contact_name, emergency_contact_phone, medical_notes),
            fetch=True
        )
        
        return {
            "success": True,
            "health_record_id": result[0]['id'],
            "student_id": student_id
        }
    
    def get_student_health_record(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Get health record for a student"""
        query = """
        SELECT 
            id,
            blood_type,
            allergies,
            chronic_conditions,
            emergency_contact_name,
            emergency_contact_phone,
            medical_notes,
            created_at,
            updated_at
        FROM student_health_records
        WHERE student_id = %s
        """
        
        result = self.db.execute_query(query, (student_id,), fetch=True)
        return result[0] if result else None
    
    # ============================================================================
    # VACCINATIONS
    # ============================================================================
    
    def record_vaccination(
        self,
        student_id: str,
        vaccine_name: str,
        administered_by: str,
        administered_date: str,
        next_dose_date: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record vaccination for a student"""
        query = """
        INSERT INTO vaccinations (
            school_id, student_id, vaccine_name, administered_by,
            administered_date, next_dose_date, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, vaccine_name, administered_by,
             administered_date, next_dose_date, notes),
            fetch=True
        )
        
        return {
            "success": True,
            "vaccination_id": result[0]['id'],
            "student_id": student_id,
            "vaccine": vaccine_name
        }
    
    def get_student_vaccinations(self, student_id: str) -> List[Dict[str, Any]]:
        """Get all vaccinations for a student"""
        query = """
        SELECT 
            id,
            vaccine_name,
            administered_by,
            administered_date,
            next_dose_date,
            notes,
            created_at
        FROM vaccinations
        WHERE student_id = %s
        ORDER BY administered_date DESC
        """
        
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    def get_upcoming_vaccinations(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get students with upcoming vaccinations"""
        query = """
        SELECT 
            v.id,
            v.student_id,
            v.vaccine_name,
            v.next_dose_date,
            s.first_name,
            s.last_name,
            s.class_name
        FROM vaccinations v
        JOIN students s ON s.id = v.student_id
        WHERE v.school_id = %s
        AND v.next_dose_date IS NOT NULL
        AND v.next_dose_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
        ORDER BY v.next_dose_date ASC
        """
        
        return self.db.execute_query(query, (self.school_id, days_ahead), fetch=True)
    
    # ============================================================================
    # SICK BAY VISITS
    # ============================================================================
    
    def record_sick_bay_visit(
        self,
        student_id: str,
        symptoms: str,
        diagnosis: Optional[str] = None,
        treatment: Optional[str] = None,
        attended_by: Optional[str] = None,
        parent_notified: bool = False
    ) -> Dict[str, Any]:
        """Record sick bay visit"""
        query = """
        INSERT INTO sick_bay_visits (
            school_id, student_id, symptoms, diagnosis, treatment,
            attended_by, parent_notified, visit_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, symptoms, diagnosis, treatment,
             attended_by, parent_notified),
            fetch=True
        )
        
        visit_id = result[0]['id']
        
        # If parent should be notified, send notification
        if parent_notified:
            # Here you would integrate with NotificationService
            pass
        
        return {
            "success": True,
            "visit_id": visit_id,
            "student_id": student_id,
            "parent_notified": parent_notified
        }
    
    def discharge_from_sick_bay(
        self,
        visit_id: str,
        discharge_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Discharge student from sick bay"""
        query = """
        UPDATE sick_bay_visits
        SET discharge_time = CURRENT_TIMESTAMP,
            discharge_notes = %s
        WHERE id = %s
        """
        
        self.db.execute_query(query, (discharge_notes, visit_id))
        
        return {
            "success": True,
            "visit_id": visit_id
        }
    
    def get_sick_bay_current_patients(self) -> List[Dict[str, Any]]:
        """Get students currently in sick bay"""
        query = """
        SELECT 
            sb.id as visit_id,
            sb.student_id,
            sb.symptoms,
            sb.diagnosis,
            sb.visit_date,
            s.first_name,
            s.last_name,
            s.class_name
        FROM sick_bay_visits sb
        JOIN students s ON s.id = sb.student_id
        WHERE sb.school_id = %s
        AND sb.discharge_time IS NULL
        ORDER BY sb.visit_date DESC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    def get_student_sick_bay_history(
        self,
        student_id: str
    ) -> List[Dict[str, Any]]:
        """Get sick bay visit history for a student"""
        query = """
        SELECT 
            id,
            symptoms,
            diagnosis,
            treatment,
            attended_by,
            visit_date,
            discharge_time,
            discharge_notes
        FROM sick_bay_visits
        WHERE student_id = %s
        ORDER BY visit_date DESC
        """
        
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    # ============================================================================
    # ANALYTICS
    # ============================================================================
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health statistics for the school"""
        # Current sick bay patients
        current_query = """
        SELECT COUNT(*) as count
        FROM sick_bay_visits
        WHERE school_id = %s AND discharge_time IS NULL
        """
        current = self.db.execute_query(current_query, (self.school_id,), fetch=True)
        
        # This month's visits
        month_query = """
        SELECT COUNT(*) as count
        FROM sick_bay_visits
        WHERE school_id = %s
        AND visit_date >= date_trunc('month', CURRENT_DATE)
        """
        month = self.db.execute_query(month_query, (self.school_id,), fetch=True)
        
        # Common illnesses
        common_query = """
        SELECT 
            diagnosis,
            COUNT(*) as count
        FROM sick_bay_visits
        WHERE school_id = %s
        AND diagnosis IS NOT NULL
        AND visit_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY diagnosis
        ORDER BY count DESC
        LIMIT 5
        """
        common = self.db.execute_query(common_query, (self.school_id,), fetch=True)
        
        # Students with chronic conditions
        chronic_query = """
        SELECT COUNT(*) as count
        FROM student_health_records
        WHERE school_id = %s
        AND chronic_conditions IS NOT NULL
        AND chronic_conditions != ''
        """
        chronic = self.db.execute_query(chronic_query, (self.school_id,), fetch=True)
        
        return {
            "success": True,
            "current_sick_bay_patients": current[0]['count'] if current else 0,
            "this_month_visits": month[0]['count'] if month else 0,
            "common_illnesses": common,
            "students_with_chronic_conditions": chronic[0]['count'] if chronic else 0
        }
    
    def get_students_with_allergies(self) -> List[Dict[str, Any]]:
        """Get all students with allergies (critical for canteen/feeding)"""
        query = """
        SELECT 
            s.id,
            s.first_name,
            s.last_name,
            s.class_name,
            hr.allergies
        FROM student_health_records hr
        JOIN students s ON s.id = hr.student_id
        WHERE hr.school_id = %s
        AND hr.allergies IS NOT NULL
        AND hr.allergies != ''
        ORDER BY s.class_name, s.first_name
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)


def get_health_service(school_id: str) -> HealthService:
    """Helper to get health service instance"""
    return HealthService(school_id)
