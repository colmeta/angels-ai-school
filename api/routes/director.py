"""
Director API Router
===================
Exposes the "Digital CEO" capabilities to the frontend Director Dashboard.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from api.agents.staff.director import DigitalCEO
from api.services.database import get_db_manager

router = APIRouter()

@router.get("/{school_id}/director/overview")
async def get_director_overview(school_id: str) -> Dict[str, Any]:
    """
    Get the high-level "One Minute Overview" for the Director.
    Delegates to the DigitalCEO agent.
    """
    try:
        # Initialize the Digital CEO Agent
        ceo = DigitalCEO()
        
        # Ask for the overview
        # The agent decides whether to use SQL (cheap) or AI (smart)
        overview = await ceo.routine_logic(
            task_type="get_school_overview",
            context={"school_id": school_id}
        )
        
        if not overview or "error" in overview:
             # If agent returns error, we might want to log it but still return structure
             # For now, return what we have
             pass
             
        return {
            "success": True,
            "data": overview
        }

    except Exception as e:
        print(f"Director API Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Director overview.")

@router.get("/{school_id}/director/trends")
async def get_director_trends(school_id: str) -> Dict[str, Any]:
    """
    Get 6-month trend data for visualizations (Fees vs Attendance).
    """
    try:
        from api.services.database import get_attendance_ops, get_fee_ops
        att_ops = get_attendance_ops()
        fee_ops = get_fee_ops()
        
        # 1. Get Monthly Attendance Trend (Real Data)
        attendance_trend = att_ops.get_attendance_trend(school_id)
        
        # 2. Get Fee Collection Summary (For current context)
        # Note: Trends for fees usually require a more specialized time-series query.
        # For now, we'll keep the existing raw SQL or use a placeholder if empty.
        db = get_db_manager()
        fees_query = """
        SELECT 
            TO_CHAR(payment_date, 'Mon') as name,
            SUM(amount) as fees
        FROM payments
        WHERE school_id = %s
        AND payment_date >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY TO_CHAR(payment_date, 'Mon'), EXTRACT(MONTH FROM payment_date)
        ORDER BY EXTRACT(MONTH FROM payment_date)
        """
        fees_trend = db.execute_query(fees_query, (school_id,), fetch=True)
        
        # Merge logic
        merged = {}
        for a in attendance_trend:
            merged[a['name']] = {'name': a['name'], 'attendance': a['attendance'], 'fees': 0}
        
        for f in fees_trend:
            if f['name'] in merged:
                merged[f['name']]['fees'] = float(f['fees'])
            else:
                merged[f['name']] = {'name': f['name'], 'attendance': 0, 'fees': float(f['fees'])}
        
        return {
            "success": True,
            "trends": list(merged.values())
        }

    except Exception as e:
        print(f"Director Trends Error: {e}")
        return {"success": False, "trends": [], "error": str(e)}
