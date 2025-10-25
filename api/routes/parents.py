from fastapi import APIRouter, HTTPException
from typing import Optional

# Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from Parent_Engagement_Service import ParentEngagementService

router = APIRouter()

@router.post("/reminders/{school_id}")
async def send_fee_reminders(school_id: str, reminder_type: str = "overdue"):
    try:
        service = ParentEngagementService(school_id)
        result = service.send_fee_reminders(reminder_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/event-broadcast/{school_id}")
async def broadcast_event(school_id: str, event_data: dict, target_grades: Optional[list] = None):
    try:
        service = ParentEngagementService(school_id)
        result = service.broadcast_event_notification(event_data, target_grades)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency/{school_id}/{student_id}")
async def send_emergency_notification(school_id: str, student_id: str, 
                                     emergency_type: str, details: str):
    try:
        service = ParentEngagementService(school_id)
        result = service.send_emergency_notification(student_id, emergency_type, details)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))