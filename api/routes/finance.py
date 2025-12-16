from fastapi import APIRouter, HTTPException
from api.services.cost_analysis import CostAnalysisService

router = APIRouter()

@router.get("/{school_id}/finance/savings-dashboard")
async def get_savings_dashboard(school_id: str):
    """
    Returns the "Money Saved" dashboard.
    Calculates savings from using digital tools (Reports, SMS, Receipts) 
    instead of paper/physical alternatives.
    """
    try:
        service = CostAnalysisService(school_id)
        dashboard = service.get_savings_dashboard()
        
        return {
            "success": True,
            "data": dashboard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
