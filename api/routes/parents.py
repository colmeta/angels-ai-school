"""
Parent Engagement Endpoints
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
from executive_assistant_service import ExecutiveAssistantService
from fastapi import APIRouter, HTTPException
from parent_engagement_service import ParentEngagementService

router = APIRouter()

@router.post("/reminders/{school_id}")
async def send_fee_reminders(school_id: str, reminder_type: str = "overdue"):
    """Send fee reminders to parents"""
    try:
        service = ParentEngagementService(school_id)
        result = service.send_fee_reminders(reminder_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/event-broadcast/{school_id}")
async def broadcast_event(school_id: str, event_data: dict, target_grades: Optional[list] = None):
    """Broadcast event to parents"""
    try:
        service = ParentEngagementService(school_id)
        result = service.broadcast_event_notification(event_data, target_grades)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency/{school_id}/{student_id}")
async def send_emergency_notification(school_id: str, student_id: str, 
                                     emergency_type: str, details: str):
    """Send emergency notification"""
    try:
        service = ParentEngagementService(school_id)
        result = service.send_emergency_notification(student_id, emergency_type, details)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
