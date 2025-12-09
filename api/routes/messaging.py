from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from api.services.database import DatabaseManager, MessageOperations
from api.core.config import get_settings

router = APIRouter()

# --- SQL Helper ---
# We need to manually instantiate DB manager or use existing dependency
def get_message_ops():
    db = DatabaseManager()
    return MessageOperations(db)

# --- Models ---
class MessageCreate(BaseModel):
    school_id: str
    recipient_type: str  # 'parent', 'student', 'staff'
    recipient_id: str
    subject: Optional[str] = "New Message"
    body: str
    message_type: str = "in_app"  # enforced to save cost
    
class MessageResponse(BaseModel):
    id: str
    subject: str
    body: str
    status: str
    created_at: datetime

# --- Endpoints ---

@router.post("/messages/send", response_model=Dict[str, Any])
def send_internal_message(msg: MessageCreate):
    """
    Send a COST-FREE internal message (In-App).
    This replaces WhatsApp/SMS for general communication.
    """
    ops = get_message_ops()
    
    # Enforce in-app type to prevent accidental costs
    payload = msg.dict()
    payload["message_type"] = "in_app"
    payload["formatted_status"] = "sent"
    payload["cost_amount"] = 0.0
    
    # Add required fields for the DB method
    # In a real scenario, we'd lookup phone/email from ID, but for in-app 
    # we just need the relation. 
    # We'll pass dummy values for phone/email if not provided, 
    # strictly for the database constraint satisfaction (if any).
    payload["recipient_phone"] = "" 
    payload["recipient_email"] = ""
    payload["template_name"] = None
    payload["template_variables"] = None
    payload["trigger_event"] = "manual_chat"
    payload["triggered_by"] = "system" # or user_id from auth
    payload["staff_id"] = None
    
    try:
        result = ops.create_message(payload)
        return {"success": True, "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/list/{school_id}/{recipient_id}")
def list_messages(school_id: str, recipient_id: str, limit: int = 50):
    """
    Get conversation history for a specific user.
    """
    db = DatabaseManager()
    
    # We need a custom query for this since MessageOperations might not have a generic list
    # that filters by recipient. Let's add a quick ad-hoc query here or extend the service.
    # For now, ad-hoc is safer than modifying the huge database.py file blindly.
    
    query = """
    SELECT * FROM messages 
    WHERE school_id = %s 
      AND recipient_id = %s
    ORDER BY created_at DESC 
    LIMIT %s
    """
    
    results = db.execute_query(query, (school_id, recipient_id, limit))
    return {"success": True, "messages": [dict(r) for r in results]}
