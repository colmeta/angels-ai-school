from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from api.services.clarity import ClarityClient
from api.services.database import (
    get_health_ops,
    get_incident_ops,
    get_inventory_ops,
    get_library_ops,
    get_transport_ops,
)


class SupportService:
    """Aggregated service for incidents, inventory, health, library, and transport operations."""

    def __init__(self, school_id: str):
        self.school_id = school_id
        self.incidents = get_incident_ops()
        self.inventory = get_inventory_ops()
        self.health = get_health_ops()
        self.library = get_library_ops()
        self.transport = get_transport_ops()

    # --- Incident Management -------------------------------------------------
    def log_incident(
        self,
        *,
        category: str,
        description: str,
        severity: str,
        reported_by: str,
        status: str = "open",
        occurred_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "school_id": self.school_id,
            "category": category,
            "description": description,
            "severity": severity,
            "status": status,
            "reported_by": reported_by,
            "occurred_at": occurred_at,
            "metadata": metadata or {},
        }
        return self.incidents.create_incident(payload)

    def list_incidents(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.incidents.list_incidents(self.school_id, limit=limit)

    # --- Inventory & Expenses ------------------------------------------------
    def adjust_inventory(
        self,
        *,
        item_name: str,
        change_quantity: float,
        reason: str,
        recorded_by: str,
        unit: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "school_id": self.school_id,
            "item_name": item_name,
            "change_quantity": change_quantity,
            "reason": reason,
            "recorded_by": recorded_by,
            "unit": unit,
            "metadata": metadata or {},
        }
        return self.inventory.record_adjustment(payload)

    def inventory_snapshot(self) -> Dict[str, Any]:
        items = self.inventory.list_items(self.school_id)
        movements = self.inventory.list_movements(self.school_id, limit=50)
        return {"items": items, "recent_movements": movements}

    # --- Sickbay / Health ----------------------------------------------------
    def record_health_visit(
        self,
        *,
        student_name: str,
        grade: Optional[str],
        symptoms: str,
        action_taken: str,
        guardian_contacted: Optional[str],
        recorded_by: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "school_id": self.school_id,
            "student_name": student_name,
            "grade": grade,
            "symptoms": symptoms,
            "action_taken": action_taken,
            "guardian_contacted": guardian_contacted,
            "recorded_by": recorded_by,
            "metadata": metadata or {},
        }
        return self.health.create_visit(payload)

    def list_health_visits(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.health.list_visits(self.school_id, limit=limit)

    # --- Library -------------------------------------------------------------
    def record_library_transaction(
        self,
        *,
        student_name: str,
        class_name: Optional[str],
        book_title: str,
        action: str,
        recorded_by: str,
        due_date: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "school_id": self.school_id,
            "student_name": student_name,
            "class_name": class_name,
            "book_title": book_title,
            "action": action,
            "due_date": due_date,
            "recorded_by": recorded_by,
            "metadata": metadata or {},
        }
        return self.library.record_transaction(payload)

    def list_library_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.library.list_transactions(self.school_id, limit=limit)

    # --- Transport -----------------------------------------------------------
    def record_transport_event(
        self,
        *,
        route_name: str,
        vehicle: Optional[str],
        status: str,
        notes: Optional[str],
        recorded_by: str,
        event_time: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "school_id": self.school_id,
            "route_name": route_name,
            "vehicle": vehicle,
            "status": status,
            "notes": notes,
            "recorded_by": recorded_by,
            "event_time": event_time or datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        return self.transport.record_event(payload)

    def list_transport_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.transport.list_events(self.school_id, limit=limit)

    # --- Consolidated Reporting ----------------------------------------------
    def generate_support_report(self) -> Dict[str, Any]:
        incidents = self.list_incidents(limit=100)
        health = self.list_health_visits(limit=100)
        transport = self.list_transport_events(limit=100)
        inventory_snapshot = self.inventory_snapshot()
        library = self.list_library_transactions(limit=100)

        clarity_payload = {
            "incidents": incidents,
            "health": health,
            "transport": transport,
            "inventory": inventory_snapshot,
            "library": library,
        }

        clarity = ClarityClient()
        try:
            summary = clarity.analyze(
                directive=(
                    "You are the Support Operations Agent. Review the provided operational logs "
                    "and produce a concise briefing covering security, health, inventory, transport, "
                    "and library activities. Highlight urgent follow-ups and celebrate wins."
                ),
                domain="education",
                files=[
                    {
                        "filename": "support_operations.json",
                        "data": json.dumps(clarity_payload, default=str),
                    }
                ],
            )
        finally:
            clarity.close()

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "incidents": incidents,
            "inventory": inventory_snapshot,
            "health": health,
            "transport": transport,
            "library": library,
            "analysis": summary,
        }
