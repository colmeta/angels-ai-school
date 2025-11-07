"""Angels AI - Executive Assistant"""
from datetime import datetime
import json
from typing import Any, Dict, List
from uuid import uuid4

from api.services.clarity import ClarityClient
from api.services.database import (
    get_document_ops,
    get_fee_ops,
    get_parent_ops,
    get_school_ops,
    get_student_ops,
)


class ExecutiveAssistant:
    """High-level orchestrator that coordinates day-to-day operations for a school."""

    def __init__(self, school_id: str):
        self.school_id = school_id
        self.students = get_student_ops()
        self.parents = get_parent_ops()
        self.fees = get_fee_ops()
        self.documents = get_document_ops()
        self.schools = get_school_ops()

    def process_registration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a student registration end-to-end."""
        try:
            student_data = data["student"]
            admission_number = student_data.get("admission_number") or f"A-{uuid4().hex[:8].upper()}"
            student_payload = {
                "school_id": self.school_id,
                "admission_number": admission_number,
                "first_name": student_data["first_name"],
                "middle_name": student_data.get("middle_name"),
                "last_name": student_data["last_name"],
                "date_of_birth": student_data["date_of_birth"],
                "gender": student_data["gender"],
                "current_grade": student_data.get("grade"),
                "current_class": student_data.get("current_class") or student_data.get("grade"),
                "admission_date": student_data.get("admission_date") or datetime.now().date(),
                "enrollment_status": student_data.get("enrollment_status", "pending"),
                "home_address": student_data.get("address"),
                "county_state": student_data.get("county"),
                "city": student_data.get("city"),
                "primary_phone": student_data.get("phone"),
                "email": student_data.get("email"),
                "blood_group": student_data.get("blood_group"),
                "allergies": student_data.get("allergies"),
                "medical_conditions": student_data.get("medical_conditions"),
                "emergency_contact_name": None,
                "emergency_contact_phone": None,
                "emergency_contact_relationship": None,
            }
            student = self.students.create_student(student_payload)

            parent_records: List[Dict[str, Any]] = []
            for parent_data in data.get("parents", []):
                parent_payload = {
                    "school_id": self.school_id,
                    "first_name": parent_data.get("first_name"),
                    "middle_name": parent_data.get("middle_name"),
                    "last_name": parent_data.get("last_name"),
                    "gender": parent_data.get("gender", "unspecified"),
                    "primary_phone": parent_data.get("phone"),
                    "secondary_phone": parent_data.get("secondary_phone"),
                    "email": parent_data.get("email"),
                    "whatsapp_number": parent_data.get("whatsapp"),
                    "preferred_language": parent_data.get("preferred_language", "en"),
                    "occupation": parent_data.get("occupation"),
                    "employer": parent_data.get("employer"),
                    "work_phone": parent_data.get("work_phone"),
                    "home_address": parent_data.get("home_address"),
                    "county_state": parent_data.get("county"),
                    "city": parent_data.get("city"),
                    "preferred_contact_method": parent_data.get("preferred_contact_method", "sms"),
                    "opt_in_notifications": parent_data.get("opt_in_notifications", True),
                }
                parent_record = self.parents.create_parent(parent_payload)
                self.parents.link_parent_to_student(
                    student_id=student["id"],
                    parent_id=parent_record["id"],
                    relationship_type=parent_data.get("relationship", "guardian"),
                    is_primary=parent_data.get("is_primary", False),
                    is_fee_payer=parent_data.get("is_fee_payer", False),
                )
                parent_records.append(parent_record)

            emergency_contact = data.get("emergency", {})
            student_update = {
                "emergency_contact_name": emergency_contact.get("name"),
                "emergency_contact_phone": emergency_contact.get("phone"),
                "emergency_contact_relationship": emergency_contact.get("relationship"),
                "enrollment_status": "active",
            }
            self.students.update_student(student["id"], student_update)

            return {
                "success": True,
                "student": student,
                "parents": parent_records,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            clarity = ClarityClient()
            try:
                fallback = clarity.analyze(
                    directive=(
                        "We attempted to register a student but encountered an error. Produce a human-readable "
                        "summary and a step-by-step remediation plan for the admin team."
                    ),
                    domain="data-entry",
                    files=[
                        {
                            "filename": "registration_payload.json",
                            "data": data,
                        }
                    ],
                )
            finally:
                clarity.close()

            return {
                "success": False,
                "error": str(exc),
                "analysis": fallback,
                "timestamp": datetime.now().isoformat(),
            }

    def get_dashboard(self) -> Dict[str, Any]:
        """Return a performance snapshot for leadership dashboards."""
        branding = self.schools.get_branding(self.school_id)
        feature_flags = self.schools.get_feature_flags(self.school_id)

        clarity = ClarityClient()
        try:
            executive_summary = clarity.analyze(
                directive=(
                    f"Produce a concise operational status report for {branding['display_name']} "
                    "covering enrollment, finance health, parent sentiment, and safety."
                ),
                domain="education",
            )
        finally:
            clarity.close()

        return {
            "school_id": self.school_id,
            "branding": branding,
            "feature_flags": feature_flags,
            "executive_summary": executive_summary,
        }

    def finalize_offline_report(self, offline_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compile offline events into a Clarity-powered report."""
        clarity = ClarityClient()
        try:
            summary = clarity.analyze(
                directive=(
                    "You are the Angels AI Digital CEO. Summarize the following offline events and "
                    "prepare action items for school leadership. Highlight critical follow-ups."
                ),
                domain="data-entry",
                files=[
                    {"filename": "offline_events.json", "data": json.dumps(offline_events, default=str)}
                ],
            )
        finally:
            clarity.close()

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "offline_events": offline_events,
            "analysis": summary,
        }
