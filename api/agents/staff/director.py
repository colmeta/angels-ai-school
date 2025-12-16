"""
The Digital CEO (Director)
==========================
Role: Strategy & Oversight
Specialty: Aggregating data into "Visual Capitalist" insights.
Optimized for: 0 Token Usage on Dashboard Loads.
"""
from typing import Dict, Any, Optional
from .base import StaffAgent
from api.services.database import FeeOperations

class DigitalCEO(StaffAgent):
    def __init__(self):
        super().__init__(role="Director", name="Dr. Clarity")

    async def routine_logic(self, task_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handles high-level dashboard queries using pure SQL/Logic.
        """
        if task_type == "get_school_overview":
            return await self._get_one_minute_overview(context.get('school_id'))
            
        if task_type == "analyze_trends":
             # In future, use SQL window functions for moving averages
             return {"trend": "stable", "message": "Trend analysis requires more data points."}
             
        return None # Fallback to AI

    async def _get_one_minute_overview(self, school_id: str) -> Dict[str, Any]:
        """
        The 'Traffic Light' Dashboard Data. 
        Cost: $0 (SQL only).
        Uses Real Database Connections.
        """
        if not school_id:
             return {"error": "School ID required for overview"}

        fees_ops = FeeOperations(self.db)
        # Using Real SQL aggregation
        # Note: If database connection fails (e.g. env var missing), this might throw.
        # StaffAgent wrapper catches exceptions.
        try:
            fee_summary = fees_ops.get_fee_collection_summary(school_id)
            
            # Calculate health score based on collection rate
            collection_rate = fee_summary.get('collection_rate_percentage', 0) or 0
            health_score = int(collection_rate) 
            
            health_status = "distressed"
            if health_score > 80: health_status = "healthy"
            elif health_score > 50: health_status = "warning"
            
            return {
                "health_score": health_score,
                "finance": {
                    "status": health_status,
                    "collection_rate": collection_rate,
                    "monthly_revenue": fee_summary.get('total_collected', 0)
                },
                "academics": {
                     "status": "warning", # Placeholder: Need GradesOperations
                     "average_grade": "B-",
                     "attendance_rate": 92
                },
                 "alerts": [] # Placeholder: Need AlertsOperations
            }
        except Exception as e:
            # Fallback for demo mode or if SQL fails
            print(f"Directory DB Error: {e}")
            return {
                "health_score": 0, 
                "error": "Could not fetch live stats.",
                "finance": {"status": "unknown"}
            }
