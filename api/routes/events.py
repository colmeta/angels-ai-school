"""
School Events API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from api.services.events import get_events_service
from api.services.calendar_sync import get_calendar_sync_service
from api.services.notifications import NotificationService

router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class EventCreate(BaseModel):
    event_name: str
    event_type: str  # sports_day, graduation, pta_meeting, parents_day, concert
    event_date: str
    start_time: str
    end_time: str
    location: str
    description: Optional[str] = None
    requires_rsvp: bool = False
    target_audience: str = 'all'
    max_attendees: Optional[int] = None


class RSVPSubmit(BaseModel):
    event_id: str
    parent_id: str
    student_id: Optional[str] = None
    response: str = 'attending'  # attending, not_attending, maybe
    number_of_guests: int = 1
    notes: Optional[str] = None


# ============================================================================
# EVENT MANAGEMENT
# ============================================================================

@router.post("/events/create")
async def create_event(school_id: str, data: EventCreate):
    """Create school event"""
    service = get_events_service(school_id)
    event_result = service.create_event(
        event_name=data.event_name,
        event_type=data.event_type,
        event_date=data.event_date,
        start_time=data.start_time,
        end_time=data.end_time,
        location=data.location,
        description=data.description,
        requires_rsvp=data.requires_rsvp,
        target_audience=data.target_audience,
        max_attendees=data.max_attendees
    )

    # AUTO-SYNC: The "Unstoppable Assistant" logic
    # Automatically sync to Google Calendar and notify all stakeholders without admin action
    if event_result.get("success"):
        cal_service = get_calendar_sync_service(school_id)
        cal_service.sync_event_to_stakeholders(event_result["event_id"])
        
        # Trigger immediate "New Event" broadcast
        # BackgroundTask could be used here to avoid blocking response
        notifier = NotificationService()
        # Logic to find all stakeholders would be inside a helper
        
    return event_result


@router.get("/events/upcoming")
async def get_upcoming_events(
    school_id: str,
    event_type: Optional[str] = None,
    days_ahead: int = 30
):
    """Get upcoming events"""
    service = get_events_service(school_id)
    return {
        "success": True,
        "events": service.get_upcoming_events(event_type, days_ahead)
    }


@router.get("/events/{event_id}")
async def get_event(school_id: str, event_id: str):
    """Get event details"""
    service = get_events_service(school_id)
    event = service.get_event_by_id(event_id)
    
    if not event:
        return {"success": False, "error": "Event not found"}
    
    return {"success": True, "event": event}


@router.patch("/events/{event_id}")
async def update_event(school_id: str, event_id: str, updates: Dict[str, Any]):
    """Update event details"""
    service = get_events_service(school_id)
    return service.update_event(event_id, updates)


@router.patch("/events/{event_id}/cancel")
async def cancel_event(school_id: str, event_id: str, reason: Optional[str] = None):
    """Cancel an event"""
    service = get_events_service(school_id)
    return service.cancel_event(event_id, reason)


# ============================================================================
# RSVP MANAGEMENT
# ============================================================================

@router.post("/events/rsvp")
async def submit_rsvp(school_id: str, data: RSVPSubmit):
    """
    Submit RSVP for an event
    
    Example:
    {
      "event_id": "abc",
      "parent_id": "xyz",
      "student_id": "123",
      "response": "attending",
      "number_of_guests": 2,
      "notes": "Will bring camera for photos"
    }
    """
    service = get_events_service(school_id)
    return service.submit_rsvp(
        event_id=data.event_id,
        parent_id=data.parent_id,
        student_id=data.student_id,
        response=data.response,
        number_of_guests=data.number_of_guests,
        notes=data.notes
    )


@router.get("/events/{event_id}/rsvps")
async def get_event_rsvps(school_id: str, event_id: str):
    """Get all RSVPs for an event"""
    service = get_events_service(school_id)
    return service.get_event_rsvps(event_id)


@router.get("/events/parent/{parent_id}/rsvps")
async def get_parent_rsvps(school_id: str, parent_id: str):
    """Get all RSVPs for a parent"""
    service = get_events_service(school_id)
    return {
        "success": True,
        "rsvps": service.get_parent_rsvps(parent_id)
    }


# ============================================================================
# ANALYTICS
# ============================================================================

@router.get("/events/calendar/{month}/{year}")
async def get_events_calendar(school_id: str, month: str, year: int):
    """Get all events for a specific month"""
    service = get_events_service(school_id)
    return service.get_events_calendar(month, year)


@router.get("/events/analytics/attendance")
async def get_attendance_stats(school_id: str):
    """Get attendance statistics for past events"""
    service = get_events_service(school_id)
    return {
        "success": True,
        "attendance_stats": service.get_event_attendance_stats()
    }
