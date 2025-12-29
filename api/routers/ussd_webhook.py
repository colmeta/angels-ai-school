"""
USSD Webhook Router
Handles USSD sessions from Africa's Talking / Twilio
"""

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.ussd import USSDService

router = APIRouter(prefix="/api/ussd", tags=["ussd"])

@router.post("/webhook", response_class=PlainTextResponse)
async def ussd_webhook(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(default="")
):
    """
    Africa's Talking USSD Webhook
    
    Example POST from Africa's Talking:
    sessionId=ATUid_xxx&serviceCode=*123*45#&phoneNumber=+256700000000&text=1*2
    """
    try:
        # Initialize USSD service
        # TODO: Get school_id from phone number mapping
        ussd_service = USSDService(school_id="demo-school")
        
        # Process USSD request
        response_text = await ussd_service.handle_ussd_request(
            session_id=sessionId,
            phone_number=phoneNumber,
            user_input=text,
            service_code=serviceCode
        )
        
        # Return plain text (Africa's Talking format)
        return response_text
    
    except Exception as e:
        # Error handling - show user-friendly message
        return f"END An error occurred. Please try again later.\nError: {str(e)}"


@router.post("/twilio/webhook", response_class=PlainTextResponse)
async def twilio_ussd_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    SessionId: str = Form(...)
):
    """
    Twilio USSD Webhook (alternative provider)
    """
    try:
        ussd_service = USSDService(school_id="demo-school")
        
        response_text = await ussd_service.handle_ussd_request(
            session_id=SessionId,
            phone_number=From,
            user_input=Body,
            service_code="*123#"  # Configured in Twilio
        )
        
        return response_text
    
    except Exception as e:
        return f"END An error occurred. Please try again."
