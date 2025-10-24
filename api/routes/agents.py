"""
AI Agents Orchestration Endpoints
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
from executive_assistant_service import ExecutiveAssistantService
from fastapi import APIRouter, HTTPException
from master_orchestrator_complete import AngelsAIMasterOrchestrator
from digital_ceo_service import DigitalCEOService

router = APIRouter()

@router.get("/daily-operations/{school_id}")
async def run_daily_operations(school_id: str):
    """Run complete daily operations"""
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        result = orchestrator.run_daily_operations()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ceo-briefing/{school_id}")
async def get_ceo_briefing(school_id: str):
    """Get CEO strategic briefing"""
    try:
        service = DigitalCEOService(school_id)
        briefing = service.generate_daily_strategic_briefing()
        return briefing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fee-collection-campaign/{school_id}")
async def launch_fee_campaign(school_id: str):
    """Launch fee collection campaign"""
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        result = orchestrator.launch_fee_collection_campaign()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-report/{school_id}")
async def get_weekly_report(school_id: str):
    """Generate weekly comprehensive report"""
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        report = orchestrator.generate_weekly_comprehensive_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
