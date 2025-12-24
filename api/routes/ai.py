"""
AI Router - Handles AI requests with three-tier support
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from api.services.r2_storage import get_r2_service
from api.core.auth import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/ai", tags=["AI"])

class AIRequest(BaseModel):
    text: str
    mode: Optional[str] = 'hybrid'  # core, hybrid, or flash
    metadata: Optional[Dict[str, Any]] = {}

class AIResponse(BaseModel):
    result_id: str
    intent: Dict[str, Any]
    mode: str
    source: str  # 'local' or 'cloud'
    processing_time: float
    synced: bool

@router.post("/parse", response_model=AIResponse)
async def parse_command(
    request: AIRequest,
    current_user = Depends(get_current_user)
):
    """
    Parse command using appropriate AI mode
    - Core: Returns with 'local' source
    - Hybrid: Processes locally, syncs to R2
    - Flash: May use cloud API if needed
    """
    result_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    # This would normally call your AI processing logic
    # For now, return a mock response
    intent = {
        "action": "attendance",
        "entity": "student",
        "extracted_data": request.text
    }
    
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    
    # For hybrid/flash modes, sync to R2
    synced = False
    if request.mode in ['hybrid', 'flash']:
        r2_service = get_r2_service()
        synced = await r2_service.upload_ai_result(
            school_id=current_user['school_id'],
            user_id=current_user['user_id'],
            result_id=result_id,
            data={
                'intent': intent,
                'mode': request.mode,
                'source': 'local',
                'processing_time': processing_time,
                'metadata': request.metadata
            }
        )
    
    return AIResponse(
        result_id=result_id,
        intent=intent,
        mode=request.mode,
        source='local',
        processing_time=processing_time,
        synced=synced
    )

@router.get("/results/{result_id}")
async def get_result(
    result_id: str,
    current_user = Depends(get_current_user)
):
    """
    Retrieve AI result from R2 cloud storage
    """
    r2_service = get_r2_service()
    
    result = await r2_service.download_ai_result(
        school_id=current_user['school_id'],
        user_id=current_user['user_id'],
        result_id=result_id
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return result

@router.get("/quota")
async def get_quota(current_user = Depends(get_current_user)):
    """
    Get storage quota status for current school
    """
    r2_service = get_r2_service()
    
    usage = await r2_service.get_storage_usage(
        school_id=current_user['school_id']
    )
    
    return usage

@router.delete("/cleanup")
async def cleanup_old_results(
    days: int = 90,
    current_user = Depends(get_current_user)
):
    """
    Delete AI results older than specified days
    """
    r2_service = get_r2_service()
    
    deleted_count = await r2_service.delete_old_results(
        school_id=current_user['school_id'],
        days=days
    )
    
    return {
        "deleted_count": deleted_count,
        "days": days,
        "message": f"Deleted {deleted_count} results older than {days} days"
    }
