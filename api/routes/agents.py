"""AI Agents Endpoints"""
from fastapi import APIRouter, HTTPException
from services.executive import ExecutiveAssistant

router = APIRouter()

@router.get("/daily-operations/{school_id}")
async def run_daily_operations(school_id: str):
    try:
        assistant = ExecutiveAssistant(school_id)
        return {
            'success': True,
            'message': 'Daily operations simulated',
            'school_id': school_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
