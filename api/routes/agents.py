from fastapi import APIRouter, HTTPException

# Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from Master_Orchestrator_Complete import AngelsAIMasterOrchestrator
from Digital_CEO_Service import DigitalCEOService

router = APIRouter()

@router.get("/daily-operations/{school_id}")
async def run_daily_operations(school_id: str):
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        result = orchestrator.run_daily_operations()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ceo-briefing/{school_id}")
async def get_ceo_briefing(school_id: str):
    try:
        service = DigitalCEOService(school_id)
        briefing = service.generate_daily_strategic_briefing()
        return briefing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fee-collection-campaign/{school_id}")
async def launch_fee_campaign(school_id: str):
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        result = orchestrator.launch_fee_collection_campaign()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-report/{school_id}")
async def get_weekly_report(school_id: str):
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        report = orchestrator.generate_weekly_comprehensive_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))