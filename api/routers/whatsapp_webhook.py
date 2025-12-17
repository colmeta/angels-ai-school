"""
WhatsApp Webhook Router
Handles incoming WhatsApp messages and status updates from Twilio
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.whatsapp import WhatsAppService

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Twilio WhatsApp Webhook
    Receives incoming messages and delivery status updates
    """
    try:
        # Get form data from Twilio
        form_data = await request.form()
        data = dict(form_data)
        
        # Extract message details
        message_type = data.get('MessageType', 'text')
        from_number = data.get('From', '').replace('whatsapp:', '')
        body = data.get('Body', '')
        message_sid = data.get('MessageSid', '')
        
        # TODO: Route to appropriate handler based on content
        # For now, log the message
        print(f"WhatsApp message from {from_number}: {body}")
        
        # Acknowledge receipt
        return JSONResponse({
            "status": "received",
            "message_sid": message_sid
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")


@router.post("/webhook/status")
async def whatsapp_status_webhook(request: Request):
    """
    Twilio WhatsApp Status Callback
    Tracks message delivery status (sent, delivered, read, failed)
    """
    try:
        form_data = await request.form()
        data = dict(form_data)
        
        message_sid = data.get('MessageSid', '')
        message_status = data.get('MessageStatus', '')  # sent, delivered, read, failed
        
        # TODO: Update database with delivery status
        print(f"WhatsApp status update: {message_sid} -> {message_status}")
        
        return JSONResponse({"status": "acknowledged"})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status webhook error: {str(e)}")


@router.post("/send")
async def send_whatsapp_message(
    to: str,
    message: str,
    school_id: str = "demo-school"  # TODO: Get from auth
):
    """
    Send a WhatsApp message
    """
    try:
        whatsapp = WhatsAppService(school_id=school_id)
        
        result = await whatsapp.send_message(
            to_number=to,
            message_body=message
        )
        
        return JSONResponse({
            "status": "success",
            "message_sid": result.get('sid'),
            "message": "Message sent successfully"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send: {str(e)}")
