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
        db = get_db_manager()
        
        # 1. Get Monthly Fee Collections (Last 6 months)
        # Using a raw query for efficiency
        fees_query = """
        SELECT 
            TO_CHAR(payment_date, 'Mon') as name,
            SUM(amount) as fees
        FROM fee_payments
        WHERE school_id = %s
        AND payment_date >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY TO_CHAR(payment_date, 'Mon'), EXTRACT(MONTH FROM payment_date)
        ORDER BY EXTRACT(MONTH FROM payment_date)
        """
        fees_data = db.execute_query(fees_query, (school_id,), fetch=True)
        
        # 2. Get Monthly Attendance Counts
        attendance_query = """
        SELECT 
            TO_CHAR(date, 'Mon') as name,
            COUNT(*) as attendance
        FROM attendance
        WHERE school_id = %s
        AND status = 'present'
        AND date >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY TO_CHAR(date, 'Mon'), EXTRACT(MONTH FROM date)
        ORDER BY EXTRACT(MONTH FROM date)
        """
        attendance_data = db.execute_query(attendance_query, (school_id,), fetch=True)
        
        # 3. Merge Data in Python (Easier than complex SQL joins for now)
        # Create a dict map for easy merging
        merged = {}
        
        for f in fees_data:
            merged[f['name']] = {'name': f['name'], 'fees': f['fees'], 'attendance': 0}
            
        for a in attendance_data:
            if a['name'] in merged:
                merged[a['name']]['attendance'] = a['attendance']
            else:
                merged[a['name']] = {'name': a['name'], 'fees': 0, 'attendance': a['attendance']}
                
        # Convert back to list sorted by month roughly (or rely on DB sort if names align)
        # For simplicity, we trust the DB order loop for now or just return values
        trend_data = list(merged.values())
        
        # Make sure we have at least some data for the chart to render
        if not trend_data:
             # Return placeholder if empty (Mock for empty state)
             # In production, we'd handle empty states in UI
             pass

        return {
            "success": True,
            "trends": trend_data
        }

    except Exception as e:
        print(f"Director Trends Error: {e}")
        # Don't crash dashboard for charts
        return {"success": False, "trends": [], "error": str(e)}
