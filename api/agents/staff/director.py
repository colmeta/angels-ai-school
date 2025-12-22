"""
The Digital CEO (Director)
==========================
Role: Strategy & Oversight
Specialty: Aggregating data into "Visual Capitalist" insights.
Optimized for: 0 Token Usage on Dashboard Loads.
"""
from typing import Dict, Any, Optional
from .base import StaffAgent
from api.services.database import get_db, get_fee_ops, get_attendance_ops, get_grades_ops

class DigitalCEO(StaffAgent):
    def __init__(self):
        super().__init__(role="Director", name="Dr. Clarity")

    async def routine_logic(self, task_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handles high-level dashboard queries using pure SQL/Logic.
        """
        if task_type == "get_school_overview":
            return await self._get_one_minute_overview(context.get('school_id'))
            
        return None # Fallback to AI for complex strategy questions

    async def _get_one_minute_overview(self, school_id: str) -> Dict[str, Any]:
        """
        The 'Traffic Light' Dashboard Data. 
        Cost: $0 for data, minimal for AI commentary.
        """
        if not school_id:
             return {"error": "School ID required for overview"}

        fee_ops = get_fee_ops()
        att_ops = get_attendance_ops()
        grade_ops = get_grades_ops()

        try:
            # 1. Financial Health
            fee_summary = fee_ops.get_fee_collection_summary(school_id)
            collection_rate = fee_summary.get('collection_rate_percentage', 0) or 0
            
            # 2. Academic & Attendance Health
            attendance_rate = att_ops.get_daily_attendance_rate(school_id)
            academic_summary = grade_ops.get_school_average_performance(school_id)
            
            # 3. Overall Health Score
            health_score = int((collection_rate + attendance_rate + academic_summary.get('average_marks', 0)) / 3)
            
            health_status = "distressed"
            if health_score > 80: health_status = "healthy"
            elif health_score > 50: health_status = "warning"
            
            overview = {
                "health_score": health_score,
                "finance": {
                    "status": "healthy" if collection_rate > 80 else "warning" if collection_rate > 50 else "distressed",
                    "collection_rate": collection_rate,
                    "monthly_revenue": fee_summary.get('total_collected', 0)
                },
                "academics": {
                     "status": "healthy" if attendance_rate > 90 else "warning",
                     "average_grade": academic_summary.get('average_grade', 'N/A'),
                     "attendance_rate": attendance_rate
                },
                "alerts": []
            }

            # 4. Digital CEO Strategic Commentary (AI Insight)
            # In a production environment, we'd use a lightweight prompt here.
            # For this build, we'll provide a data-driven summary.
            insight = f"Directorial Insight: School health is at {health_score}%. "
            if collection_rate < 70:
                insight += "Focus on fee collection this week."
            elif attendance_rate < 85:
                insight += "Attendance is lagging; check for specific class drops."
            else:
                insight += "Operations are stable. Ready for mid-term expansion."
            
            overview["strategic_insight"] = insight
            
            return overview
        except Exception as e:
            # Fallback for demo mode or if SQL fails
            print(f"Directory DB Error: {e}")
            return {
                "health_score": 0, 
                "error": "Could not fetch live stats.",
                "finance": {"status": "unknown"}
            }
