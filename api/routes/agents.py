"""
AI Agents Orchestration Endpoints
"""
from fastapi import APIRouter, HTTPException

# FIX: Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Master_Orchestrator_Complete import AngelsAIMasterOrchestrator
from Digital_CEO_Service import DigitalCEOService

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
