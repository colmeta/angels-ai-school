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

@router.get("/defaulters")
async def get_fee_defaulters(school_id: str):
    """
    Get list of fee defaulters for load testing.
    """
    try:
        from api.services.database import DatabaseManager
        db = DatabaseManager()
        
        # Schema: student_fees.payment_status = 'pending' or balance > 0
        # We need to join with students to get names
        query = """
        SELECT s.id, s.first_name, s.last_name, s.admission_number, sf.balance, sf.total_fees
        FROM student_fees sf
        JOIN students s ON sf.student_id = s.id
        WHERE s.school_id = %s
        AND sf.balance > 0
        LIMIT 100
        """
        
        results = db.execute_query(query, (school_id,))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'db' in locals():
            db.close_all_connections()
