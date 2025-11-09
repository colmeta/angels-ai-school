"""
Alumni Tracking Service
Alumni database, career tracking, networking, mentorship programs
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.services.database import get_db_manager


class AlumniService:
    """Service for alumni management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    def register_alumni(
        self,
        first_name: str,
        last_name: str,
        graduation_year: int,
        graduation_class: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        current_occupation: Optional[str] = None,
        employer: Optional[str] = None,
        university_attended: Optional[str] = None,
        degree_obtained: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register an alumnus"""
        query = """
        INSERT INTO alumni (
            school_id, first_name, last_name, graduation_year, graduation_class,
            email, phone, current_occupation, employer, university_attended, degree_obtained
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, first_name, last_name, graduation_year, graduation_class,
             email, phone, current_occupation, employer, university_attended, degree_obtained),
            fetch=True
        )
        
        return {
            "success": True,
            "alumni_id": result[0]['id'],
            "name": f"{first_name} {last_name}",
            "graduation_year": graduation_year
        }
    
    def update_alumni_info(
        self,
        alumni_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update alumni information"""
        allowed_fields = [
            'email', 'phone', 'current_occupation', 'employer',
            'university_attended', 'degree_obtained', 'achievements', 'linkedin_url'
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
        UPDATE alumni
        SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND school_id = %s
        """
        
        values.extend([alumni_id, self.school_id])
        self.db.execute_query(query, tuple(values))
        
        return {"success": True, "alumni_id": alumni_id}
    
    def search_alumni(
        self,
        graduation_year: Optional[int] = None,
        occupation: Optional[str] = None,
        university: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search alumni by criteria"""
        query = """
        SELECT 
            id, first_name, last_name, graduation_year, graduation_class,
            email, phone, current_occupation, employer, university_attended
        FROM alumni
        WHERE school_id = %s
        """
        
        params = [self.school_id]
        
        if graduation_year:
            query += " AND graduation_year = %s"
            params.append(graduation_year)
        
        if occupation:
            query += " AND current_occupation ILIKE %s"
            params.append(f"%{occupation}%")
        
        if university:
            query += " AND university_attended ILIKE %s"
            params.append(f"%{university}%")
        
        query += " ORDER BY graduation_year DESC, last_name"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_alumni_statistics(self) -> Dict[str, Any]:
        """Get alumni statistics"""
        total_query = """
        SELECT 
            COUNT(*) as total_alumni,
            COUNT(CASE WHEN university_attended IS NOT NULL THEN 1 END) as university_attendees,
            COUNT(CASE WHEN current_occupation IS NOT NULL THEN 1 END) as employed
        FROM alumni
        WHERE school_id = %s
        """
        total = self.db.execute_query(total_query, (self.school_id,), fetch=True)
        
        by_year_query = """
        SELECT 
            graduation_year,
            COUNT(*) as count
        FROM alumni
        WHERE school_id = %s
        GROUP BY graduation_year
        ORDER BY graduation_year DESC
        LIMIT 10
        """
        by_year = self.db.execute_query(by_year_query, (self.school_id,), fetch=True)
        
        top_employers_query = """
        SELECT 
            employer,
            COUNT(*) as count
        FROM alumni
        WHERE school_id = %s AND employer IS NOT NULL
        GROUP BY employer
        ORDER BY count DESC
        LIMIT 10
        """
        top_employers = self.db.execute_query(top_employers_query, (self.school_id,), fetch=True)
        
        return {
            "success": True,
            "overview": total[0] if total else {},
            "by_graduation_year": by_year,
            "top_employers": top_employers
        }


def get_alumni_service(school_id: str) -> AlumniService:
    """Helper to get alumni service instance"""
    return AlumniService(school_id)
