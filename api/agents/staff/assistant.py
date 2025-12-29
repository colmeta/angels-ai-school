"""
The Executive Assistant (Daily Coordinator)
===========================================
Role: Operations & Coordination
Specialty: Daily digests, event tracking, and task management.
Optimized for: 0 Token Usage on Daily Snapshots.
"""
from typing import Any, Dict, Optional
from api.services.database import get_db_manager
from .base import StaffAgent

class Assistant(StaffAgent):
    def __init__(self):
        super().__init__(role="Executive Assistant", name="Angel")

    async def routine_logic(self, task_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        school_id = context.get('school_id')
        if not school_id:
            return None

        db = get_db_manager()

        if task_type == "daily_digest":
            try:
                # Combine multiple queries into one logic block
                stats = {
                    "new_students": db.execute_query(
                        "SELECT COUNT(*) as count FROM students WHERE school_id = %s AND enrollment_date = CURRENT_DATE",
                        (school_id,), fetch=True
                    )[0]["count"],
                    "fee_payments": db.execute_query(
                        "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM payments WHERE school_id = %s AND payment_date = CURRENT_DATE",
                        (school_id,), fetch=True
                    )[0],
                    "incidents": db.execute_query(
                        "SELECT COUNT(*) as count FROM incidents WHERE school_id = %s AND DATE(incident_date) = CURRENT_DATE",
                        (school_id,), fetch=True
                    )[0]["count"],
                    "health_visits": db.execute_query(
                        "SELECT COUNT(*) as count FROM health_visits WHERE school_id = %s AND DATE(visit_date) = CURRENT_DATE",
                        (school_id,), fetch=True
                    )[0]["count"]
                }
                return stats
            except Exception as e:
                print(f"Assistant Digest Error: {e}")
                return None
        
        return None # Fallback to AI
