"""UNEB integration routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/uneb/status")
async def uneb_status():
    """Check UNEB integration status"""
    return {"status": "available", "message": "UNEB service ready"}
