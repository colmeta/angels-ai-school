"""
Disciplinary Records Service
Incident tracking, warnings, suspensions, behavior monitoring
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.services.database import get_db_manager


class DisciplineService:
    """Service for disciplinary records and behavior tracking"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # DISCIPLINARY INCIDENTS
    # ============================================================================
    
    def record_incident(
        self,
        student_id: str,
        incident_type: str,  # fighting, bullying, theft, disrespect, absenteeism, etc.
        description: str,
        severity: str,  # minor, moderate, serious
        reported_by: str,
        incident_date: str,
        witnesses: Optional[List[str]] = None,
        action_taken: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record disciplinary incident"""
        query = """
        INSERT INTO disciplinary_incidents (
            school_id, student_id, incident_type, description, severity,
            reported_by, incident_date, witnesses, action_taken
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, incident_type, description, severity,
             reported_by, incident_date, witnesses, action_taken),
            fetch=True
        )
        
        # Check if student needs escalation (multiple incidents)
        count_query = """
        SELECT COUNT(*) as count
        FROM disciplinary_incidents
        WHERE student_id = %s
        AND incident_date >= CURRENT_DATE - INTERVAL '30 days'
        """
        
        recent_incidents = self.db.execute_query(count_query, (student_id,), fetch=True)
        incident_count = recent_incidents[0]['count'] if recent_incidents else 0
        
        escalation_needed = incident_count >= 3
        
        return {
            "success": True,
            "incident_id": result[0]['id'],
            "student_id": student_id,
            "severity": severity,
            "recent_incident_count": incident_count,
            "escalation_needed": escalation_needed
        }
    
    def update_incident_resolution(
        self,
        incident_id: str,
        action_taken: str,
        resolved: bool = True
    ) -> Dict[str, Any]:
        """Update incident with action taken and resolution"""
        query = """
        UPDATE disciplinary_incidents
        SET action_taken = %s,
            resolved = %s,
            resolved_at = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE NULL END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        self.db.execute_query(query, (action_taken, resolved, resolved, incident_id))
        
        return {
            "success": True,
            "incident_id": incident_id,
            "resolved": resolved
        }
    
    def get_student_incidents(
        self,
        student_id: str,
        include_resolved: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all incidents for a student"""
        query = """
        SELECT 
            id,
            incident_type,
            description,
            severity,
            reported_by,
            incident_date,
            action_taken,
            resolved,
            resolved_at
        FROM disciplinary_incidents
        WHERE student_id = %s
        """
        
        if not include_resolved:
            query += " AND resolved = false"
        
        query += " ORDER BY incident_date DESC"
        
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    def get_unresolved_incidents(self) -> List[Dict[str, Any]]:
        """Get all unresolved incidents"""
        query = """
        SELECT 
            di.id,
            di.student_id,
            di.incident_type,
            di.description,
            di.severity,
            di.incident_date,
            s.first_name,
            s.last_name,
            s.class_name
        FROM disciplinary_incidents di
        JOIN students s ON s.id = di.student_id
        WHERE di.school_id = %s
        AND di.resolved = false
        ORDER BY 
            CASE di.severity
                WHEN 'serious' THEN 1
                WHEN 'moderate' THEN 2
                WHEN 'minor' THEN 3
            END,
            di.incident_date DESC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    # ============================================================================
    # SUSPENSIONS
    # ============================================================================
    
    def create_suspension(
        self,
        student_id: str,
        reason: str,
        start_date: str,
        end_date: str,
        suspended_by: str,
        related_incident_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create suspension record"""
        query = """
        INSERT INTO suspensions (
            school_id, student_id, reason, start_date, end_date,
            suspended_by, related_incident_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, student_id, reason, start_date, end_date,
             suspended_by, related_incident_id),
            fetch=True
        )
        
        # Notify parents (integrate with NotificationService)
        # This would send SMS/email to parents about suspension
        
        return {
            "success": True,
            "suspension_id": result[0]['id'],
            "student_id": student_id,
            "start_date": start_date,
            "end_date": end_date
        }
    
    def end_suspension(
        self,
        suspension_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark suspension as completed"""
        query = """
        UPDATE suspensions
        SET status = 'completed',
            return_notes = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        self.db.execute_query(query, (notes, suspension_id))
        
        return {
            "success": True,
            "suspension_id": suspension_id,
            "status": "completed"
        }
    
    def get_active_suspensions(self) -> List[Dict[str, Any]]:
        """Get all active suspensions"""
        query = """
        SELECT 
            su.id,
            su.student_id,
            su.reason,
            su.start_date,
            su.end_date,
            s.first_name,
            s.last_name,
            s.class_name
        FROM suspensions su
        JOIN students s ON s.id = su.student_id
        WHERE su.school_id = %s
        AND su.status = 'active'
        AND su.end_date >= CURRENT_DATE
        ORDER BY su.end_date ASC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)
    
    def get_student_suspensions(self, student_id: str) -> List[Dict[str, Any]]:
        """Get suspension history for a student"""
        query = """
        SELECT 
            id,
            reason,
            start_date,
            end_date,
            status,
            suspended_by,
            return_notes
        FROM suspensions
        WHERE student_id = %s
        ORDER BY start_date DESC
        """
        
        return self.db.execute_query(query, (student_id,), fetch=True)
    
    # ============================================================================
    # ANALYTICS & REPORTS
    # ============================================================================
    
    def get_behavior_summary(self, student_id: str) -> Dict[str, Any]:
        """Get behavior summary for a student"""
        # Count incidents by severity
        incidents_query = """
        SELECT 
            severity,
            COUNT(*) as count
        FROM disciplinary_incidents
        WHERE student_id = %s
        GROUP BY severity
        """
        incidents = self.db.execute_query(incidents_query, (student_id,), fetch=True)
        
        # Count suspensions
        suspensions_query = """
        SELECT COUNT(*) as count
        FROM suspensions
        WHERE student_id = %s
        """
        suspensions = self.db.execute_query(suspensions_query, (student_id,), fetch=True)
        
        # Get recent incidents
        recent_query = """
        SELECT 
            incident_type,
            incident_date,
            severity
        FROM disciplinary_incidents
        WHERE student_id = %s
        ORDER BY incident_date DESC
        LIMIT 5
        """
        recent = self.db.execute_query(recent_query, (student_id,), fetch=True)
        
        return {
            "success": True,
            "student_id": student_id,
            "incidents_by_severity": {i['severity']: i['count'] for i in incidents},
            "total_suspensions": suspensions[0]['count'] if suspensions else 0,
            "recent_incidents": recent
        }
    
    def get_school_discipline_statistics(self) -> Dict[str, Any]:
        """Get discipline statistics for the school"""
        # Total incidents this term
        incidents_query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN severity = 'serious' THEN 1 END) as serious,
            COUNT(CASE WHEN severity = 'moderate' THEN 1 END) as moderate,
            COUNT(CASE WHEN severity = 'minor' THEN 1 END) as minor
        FROM disciplinary_incidents
        WHERE school_id = %s
        AND incident_date >= CURRENT_DATE - INTERVAL '90 days'
        """
        incidents = self.db.execute_query(incidents_query, (self.school_id,), fetch=True)
        
        # Common incident types
        common_query = """
        SELECT 
            incident_type,
            COUNT(*) as count
        FROM disciplinary_incidents
        WHERE school_id = %s
        AND incident_date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY incident_type
        ORDER BY count DESC
        LIMIT 5
        """
        common = self.db.execute_query(common_query, (self.school_id,), fetch=True)
        
        # Active suspensions
        suspensions_query = """
        SELECT COUNT(*) as count
        FROM suspensions
        WHERE school_id = %s AND status = 'active'
        """
        suspensions = self.db.execute_query(suspensions_query, (self.school_id,), fetch=True)
        
        return {
            "success": True,
            "incidents_last_90_days": incidents[0] if incidents else {},
            "common_incident_types": common,
            "active_suspensions": suspensions[0]['count'] if suspensions else 0
        }
    
    def get_students_at_risk(self) -> List[Dict[str, Any]]:
        """
        Get students at risk (multiple incidents, pattern of behavior)
        For intervention programs
        """
        query = """
        SELECT 
            s.id,
            s.first_name,
            s.last_name,
            s.class_name,
            COUNT(di.id) as incident_count,
            COUNT(CASE WHEN di.severity = 'serious' THEN 1 END) as serious_count,
            MAX(di.incident_date) as last_incident_date
        FROM students s
        JOIN disciplinary_incidents di ON di.student_id = s.id
        WHERE s.school_id = %s
        AND di.incident_date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY s.id, s.first_name, s.last_name, s.class_name
        HAVING COUNT(di.id) >= 3 OR COUNT(CASE WHEN di.severity = 'serious' THEN 1 END) >= 1
        ORDER BY incident_count DESC, serious_count DESC
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)


def get_discipline_service(school_id: str) -> DisciplineService:
    """Helper to get discipline service instance"""
    return DisciplineService(school_id)
