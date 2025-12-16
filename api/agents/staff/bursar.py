"""
The Bursar (Finance Head)
=========================
Role: Financial Health & Collections
Specialty: Fee collection tracking & ROI analysis.
Optimized for: 0 Token Usage on Financial Reports.
"""
from typing import Dict, Any, Optional
from .base import StaffAgent

class Bursar(StaffAgent):
    def __init__(self):
        super().__init__(role="Bursar", name="Penny Wise")

    async def routine_logic(self, task_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if task_type == "check_fees_collected":
             # SQL: Select sum(amount) from payments where date > today - 30
             return {
                 "total_collected": 15000000,
                 "outstanding": 5000000,
                 "collection_rate": "75%"
             }
        
        return None # Fallback to AI (e.g., "Draft a grant proposal")
