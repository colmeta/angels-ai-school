"""
The Headteacher (Academic Head)
===============================
Role: Academic Standards & Teacher Performance
Specialty: Class performance analysis & Parent communication.
Optimized for: 0 Token Usage on Routine Checks.
"""
from typing import Any, Dict, Optional
from api.services.database import get_grades_ops
from .base import StaffAgent

class Headteacher(StaffAgent):
    def __init__(self):
        super().__init__(role="Headteacher", name="Master Vision")

    async def routine_logic(self, task_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        school_id = context.get('school_id')
        if not school_id:
            return None

        if task_type == "check_class_performance":
             class_name = context.get("class_name")
             if not class_name:
                 return None
                 
             grade_ops = get_grades_ops()
             try:
                 perf = grade_ops.get_class_performance(school_id, class_name)
                 return {
                     "class": class_name,
                     "average": perf["average"],
                     "at_risk_count": perf["at_risk_count"],
                     "flagged_student_ids": perf["flagged_student_ids"]
                 }
             except Exception as e:
                 print(f"Headteacher performance error: {e}")
                 return None
        
        return None # Fallback to AI
