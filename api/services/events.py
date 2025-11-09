"""
School Events Service
Events calendar, RSVP tracking, parent participation
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from api.services.database import get_db_manager


class EventsService:
    """Service for school events management"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # EVENT MANAGEMENT
    # ============================================================================
    
    def create_event(
        self,
        event_name: str,
        event_type: str,  # sports_day, graduation, pta_meeting, parents_day, concert, etc.
        event_date: str,
        start_time: str,
        end_time: str,
        location: str,
        description: Optional[str] = None,
        requires_rsvp: bool = False,
        target_audience: str = 'all',  # all, parents, students, specific_class
        max_attendees: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create school event"""
        query = """
        INSERT INTO school_events (
            school_id, event_name, event_type, event_date, start_time,
            end_time, location, description, requires_rsvp, target_audience, max_attendees
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, event_name, event_type, event_date, start_time,
             end_time, location, description, requires_rsvp, target_audience, max_attendees),
            fetch=True
        )
        
        # Notify stakeholders (integrate with NotificationService)
        # Send notifications to parents/students about new event
        
        return {
            "success": True,
            "event_id": result[0]['id'],
            "event_name": event_name,
            "event_date": event_date
        }
    
    def get_upcoming_events(
        self,
        event_type: Optional[str] = None,
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """Get upcoming events"""
        query = """
        SELECT 
            id,
            event_name,
            event_type,
            event_date,
            start_time,
            end_time,
            location,
            description,
            requires_rsvp,
            target_audience,
            max_attendees,
            status
        FROM school_events
        WHERE school_id = %s
        AND event_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
        """
        
        params = [self.school_id, days_ahead]
        
        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)
        
        query += " ORDER BY event_date ASC, start_time ASC"
        
        return self.db.execute_query(query, tuple(params), fetch=True)
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event details"""
        query = """
        SELECT 
            id,
            event_name,
            event_type,
            event_date,
            start_time,
            end_time,
            location,
            description,
            requires_rsvp,
            target_audience,
            max_attendees,
            status,
            created_at
        FROM school_events
        WHERE id = %s
        """
        
        result = self.db.execute_query(query, (event_id,), fetch=True)
        return result[0] if result else None
    
    def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update event details"""
        allowed_fields = [
            'event_name', 'event_date', 'start_time', 'end_time',
            'location', 'description', 'max_attendees', 'status'
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
        UPDATE school_events
        SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND school_id = %s
        """
        
        values.extend([event_id, self.school_id])
        self.db.execute_query(query, tuple(values))
        
        return {"success": True, "event_id": event_id}
    
    def cancel_event(self, event_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an event"""
        query = """
        UPDATE school_events
        SET status = 'cancelled',
            description = COALESCE(description, '') || %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND school_id = %s
        """
        
        cancellation_note = f"\n\nEvent cancelled. Reason: {reason}" if reason else "\n\nEvent cancelled."
        self.db.execute_query(query, (cancellation_note, event_id, self.school_id))
        
        # Notify all attendees about cancellation
        
        return {
            "success": True,
            "event_id": event_id,
            "status": "cancelled"
        }
    
    # ============================================================================
    # RSVP MANAGEMENT
    # ============================================================================
    
    def submit_rsvp(
        self,
        event_id: str,
        parent_id: str,
        student_id: Optional[str] = None,
        response: str = 'attending',  # attending, not_attending, maybe
        number_of_guests: int = 1,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit RSVP for an event"""
        # Check if event requires RSVP
        event = self.get_event_by_id(event_id)
        
        if not event:
            return {"success": False, "error": "Event not found"}
        
        if not event['requires_rsvp']:
            return {"success": False, "error": "Event does not require RSVP"}
        
        # Check capacity
        if event['max_attendees'] and response == 'attending':
            count_query = """
            SELECT SUM(number_of_guests) as total
            FROM event_rsvp
            WHERE event_id = %s AND response = 'attending'
            """
            current = self.db.execute_query(count_query, (event_id,), fetch=True)
            current_attendees = int(current[0]['total'] or 0) if current else 0
            
            if current_attendees + number_of_guests > event['max_attendees']:
                return {"success": False, "error": "Event is at full capacity"}
        
        # Create/update RSVP
        query = """
        INSERT INTO event_rsvp (
            school_id, event_id, parent_id, student_id, response, number_of_guests, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_id, parent_id, student_id) DO UPDATE
        SET response = EXCLUDED.response,
            number_of_guests = EXCLUDED.number_of_guests,
            notes = EXCLUDED.notes,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        result = self.db.execute_query(
            query,
            (self.school_id, event_id, parent_id, student_id, response, number_of_guests, notes),
            fetch=True
        )
        
        return {
            "success": True,
            "rsvp_id": result[0]['id'],
            "event_id": event_id,
            "response": response
        }
    
    def get_event_rsvps(self, event_id: str) -> Dict[str, Any]:
        """Get all RSVPs for an event"""
        query = """
        SELECT 
            er.id,
            er.parent_id,
            er.student_id,
            er.response,
            er.number_of_guests,
            er.notes,
            p.first_name as parent_first_name,
            p.last_name as parent_last_name,
            s.first_name as student_first_name,
            s.last_name as student_last_name
        FROM event_rsvp er
        JOIN parents p ON p.id = er.parent_id
        LEFT JOIN students s ON s.id = er.student_id
        WHERE er.event_id = %s
        ORDER BY er.response, p.last_name
        """
        
        rsvps = self.db.execute_query(query, (event_id,), fetch=True)
        
        # Calculate summary
        attending = sum(r['number_of_guests'] for r in rsvps if r['response'] == 'attending')
        not_attending = sum(r['number_of_guests'] for r in rsvps if r['response'] == 'not_attending')
        maybe = sum(r['number_of_guests'] for r in rsvps if r['response'] == 'maybe')
        
        return {
            "success": True,
            "event_id": event_id,
            "summary": {
                "attending": attending,
                "not_attending": not_attending,
                "maybe": maybe,
                "total_responses": len(rsvps)
            },
            "rsvps": rsvps
        }
    
    def get_parent_rsvps(self, parent_id: str) -> List[Dict[str, Any]]:
        """Get all RSVPs for a parent"""
        query = """
        SELECT 
            er.id,
            er.event_id,
            er.response,
            er.number_of_guests,
            se.event_name,
            se.event_type,
            se.event_date,
            se.start_time,
            se.location
        FROM event_rsvp er
        JOIN school_events se ON se.id = er.event_id
        WHERE er.parent_id = %s
        ORDER BY se.event_date DESC
        """
        
        return self.db.execute_query(query, (parent_id,), fetch=True)
    
    # ============================================================================
    # ANALYTICS
    # ============================================================================
    
    def get_events_calendar(self, month: str, year: int) -> Dict[str, Any]:
        """Get all events for a specific month"""
        query = """
        SELECT 
            id,
            event_name,
            event_type,
            event_date,
            start_time,
            location,
            status
        FROM school_events
        WHERE school_id = %s
        AND EXTRACT(MONTH FROM event_date) = %s
        AND EXTRACT(YEAR FROM event_date) = %s
        ORDER BY event_date, start_time
        """
        
        month_num = datetime.strptime(month, '%B').month if month.isalpha() else int(month)
        
        events = self.db.execute_query(query, (self.school_id, month_num, year), fetch=True)
        
        return {
            "success": True,
            "month": month,
            "year": year,
            "events": events,
            "total_events": len(events)
        }
    
    def get_event_attendance_stats(self) -> List[Dict[str, Any]]:
        """Get attendance statistics for past events"""
        query = """
        SELECT 
            se.id,
            se.event_name,
            se.event_date,
            se.max_attendees,
            COUNT(er.id) as total_responses,
            SUM(CASE WHEN er.response = 'attending' THEN er.number_of_guests ELSE 0 END) as total_attending
        FROM school_events se
        LEFT JOIN event_rsvp er ON er.event_id = se.id
        WHERE se.school_id = %s
        AND se.event_date < CURRENT_DATE
        AND se.requires_rsvp = true
        GROUP BY se.id, se.event_name, se.event_date, se.max_attendees
        ORDER BY se.event_date DESC
        LIMIT 10
        """
        
        return self.db.execute_query(query, (self.school_id,), fetch=True)


def get_events_service(school_id: str) -> EventsService:
    """Helper to get events service instance"""
    return EventsService(school_id)
