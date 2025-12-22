"""
The Bursar (Finance Head)
=========================
Role: Financial Health & Collections
Specialty: Fee collection tracking & ROI analysis.
Optimized for: 0 Token Usage on Financial Reports.
"""
from typing import Any, Dict, Optional
from api.services.database import get_fee_ops
from .base import StaffAgent

class Bursar(StaffAgent):
    def __init__(self):
        super().__init__(role="Bursar", name="Penny Wise")

    async def routine_logic(self, task_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        school_id = context.get('school_id')
        if not school_id:
            return None

        fee_ops = get_fee_ops()

        if task_type == "check_fees_collected":
            try:
                summary = fee_ops.get_fee_collection_summary(school_id)
                return {
                    "total_collected": float(summary.get('total_collected', 0) or 0),
                    "outstanding": float(summary.get('total_outstanding', 0) or 0),
                    "collection_rate": f"{summary.get('collection_rate_percentage', 0)}%"
                }
            except Exception as e:
                print(f"Bursar Analytics Error: {e}")
                return None
        
        if task_type == "get_overdue_list":
            try:
                overdue = fee_ops.get_overdue_fees(school_id)
                return {
                    "count": len(overdue),
                    "total_overdue_amount": sum(float(f['balance']) for f in overdue if f.get('balance')),
                    "top_defaulters": overdue[:5] # Return first 5 for AI processing
                }
            except Exception as e:
                print(f"Bursar Overdue Error: {e}")
                return None
        
        return None # Fallback to AI
