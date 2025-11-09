"""USSD service routes"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/ussd")
async def ussd_endpoint():
    """USSD service endpoint"""
    return {"status": "available", "message": "USSD service ready"}
