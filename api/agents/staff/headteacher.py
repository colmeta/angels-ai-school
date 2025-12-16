"""
The Headteacher (Academic Head)
===============================
Role: Academic Standards & Teacher Performance
Specialty: Class performance analysis & Parent communication.
Optimized for: 0 Token Usage on Routine Checks.
"""
from typing import Dict, Any, Optional
from .base import StaffAgent

class Headteacher(StaffAgent):
    def __init__(self):
        super().__init__(role="Headteacher", name="Master Vision")

    async def routine_logic(self, task_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if task_type == "check_class_performance":
             # SQL: Select avg(grade) from grades where class = X
             return {
                 "class": context.get("class_name"),
                 "average": 78, 
                 "trend": "up",
                 "flagged_students": ["John Doe", "Jane Smith"]
             }
        
        return None # Fallback to AI (e.g., "Write a disciplinary letter")
