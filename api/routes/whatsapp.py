"""WhatsApp integration routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/whatsapp/status")
async def whatsapp_status():
    """Check WhatsApp integration status"""
    return {"status": "available", "message": "WhatsApp service ready"}
