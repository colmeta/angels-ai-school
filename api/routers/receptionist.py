"""
24/7 AI Receptionist - Embeddable Chatbot Widget
Provides instant support for parents, students, and visitors
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.clarity import get_clarity_client

router = APIRouter(prefix="/api/receptionist", tags=["ai-receptionist"])

class ChatMessage(BaseModel):
    message: str
    school_id: str
    session_id: Optional[str] = None
    user_type: Optional[str] = "visitor"  # visitor, parent, student

class ReceptionistResponse(BaseModel):
    reply: str
    suggestions: List[str]
    session_id: str


@router.post("/chat", response_model=ReceptionistResponse)
async def chat_with_receptionist(msg: ChatMessage):
    """
    24/7 AI Receptionist - answers common questions
    
    Common queries:
    - "What are your school fees?"
    - "How do I register my child?"
    - "What are school hours?"
    - "How can I contact the director?"
    """
    try:
        # Get Clarity AI client
        clarity = get_clarity_client()
        
        # Build context about the school
        context = f"""
        You are a helpful AI receptionist for a school (ID: {msg.school_id}).
        You help parents, students, and visitors with common questions.
        
        Be professional, friendly, and concise.
        If you don't know something, guide them to contact the school office.
        
        Common information you can help with:
        - School hours: Monday-Friday 7:00 AM - 4:00 PM
        - Admissions process: Visit /signup or contact admissions office
        - Fee payment: Available via school portal or mobile money
        - Contact: Call school office or visit campus
        
        User type: {msg.user_type}
        User question: {msg.message}
        """
        
        # Get AI response
        response = await clarity.generate_response(
            prompt=context,
            max_tokens=200
        )
        
        # Generate helpful suggestions
        suggestions = _generate_suggestions(msg.message)
        
        return ReceptionistResponse(
            reply=response.get('text', 'How can I help you today?'),
            suggestions=suggestions,
            session_id=msg.session_id or _generate_session_id()
        )
    
    except Exception as e:
        # Fallback to rule-based responses
        return ReceptionistResponse(
            reply=_fallback_response(msg.message),
            suggestions=["Check school fees", "Contact admissions", "View school calendar"],
            session_id=msg.session_id or _generate_session_id()
        )


def _generate_suggestions(message: str) -> List[str]:
    """Generate contextual suggestions based on user message"""
    message_lower = message.lower()
    
    if 'fee' in message_lower or 'pay' in message_lower:
        return ["View fee structure", "Payment methods", "Request invoice"]
    elif 'register' in message_lower or 'enroll' in message_lower or 'admission' in message_lower:
        return ["Admission requirements", "Registration process", "Required documents"]
    elif 'contact' in message_lower or 'phone' in message_lower:
        return ["School phone", "Email address", "Visit campus"]
    elif 'time' in message_lower or 'hours' in message_lower or 'schedule' in message_lower:
        return ["School hours", "Term calendar", "Event schedule"]
    else:
        return ["School fees", "Admissions", "Contact us", "School calendar"]


def _fallback_response(message: str) -> str:
    """Rule-based fallback when AI is unavailable"""
    message_lower = message.lower()
    
    if 'fee' in message_lower:
        return "Our school fees vary by grade level. Please visit the Admissions Office or call us for detailed fee structure."
    elif 'register' in message_lower or 'enroll' in message_lower:
        return "To register your child, please visit our admissions page or contact the school office. You can also sign up online at /signup."
    elif 'contact' in message_lower:
        return "You can reach us at the school office during business hours (Mon-Fri, 7 AM - 4 PM) or visit our campus."
    elif 'time' in message_lower or 'hours' in message_lower:
        return "School hours are Monday to Friday, 7:00 AM to 4:00 PM. Classes start at 8:00 AM."
    else:
        return "Hello! I'm the school AI receptionist. How can I help you today? You can ask about fees, admissions, contact information, or school hours."


def _generate_session_id() -> str:
    """Generate unique session ID"""
    import uuid
    return str(uuid.uuid4())


@router.get("/widget-config/{school_id}")
async def get_widget_config(school_id: str):
    """
    Get chatbot widget configuration for a school
    Returns branding, position, greeting message
    """
    try:
        # TODO: Fetch from database
        return {
            "school_id": school_id,
            "enabled": True,
            "position": "bottom-right",
            "primary_color": "#2563eb",
            "greeting": "Hello! How can I help you today?",
            "avatar_url": "https://cdn.angels-ai.com/receptionist-avatar.png",
            "office_hours": "Mon-Fri, 7 AM - 4 PM"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
