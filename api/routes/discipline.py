"""
Disciplinary Records API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from api.services.discipline import get_discipline_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class IncidentRecord(BaseModel):
    student_id: str
    incident_type: str  # fighting, bullying, theft, disrespect, absenteeism
    description: str
    severity: str  # minor, moderate, serious
    reported_by: str
    incident_date: str
    witnesses: Optional[List[str]] = None
    action_taken: Optional[str] = None


class IncidentUpdate(BaseModel):
    action_taken: str
    resolved: bool = True


class SuspensionCreate(BaseModel):
    student_id: str
    reason: str
    start_date: str
    end_date: str
    suspended_by: str
    related_incident_id: Optional[str] = None


# ============================================================================
# DISCIPLINARY INCIDENTS
# ============================================================================

@router.post("/discipline/incidents/record")
async def record_incident(school_id: str, data: IncidentRecord):
    """Record disciplinary incident"""
    service = get_discipline_service(school_id)
    return service.record_incident(
        student_id=data.student_id,
        incident_type=data.incident_type,
        description=data.description,
        severity=data.severity,
        reported_by=data.reported_by,
        incident_date=data.incident_date,
        witnesses=data.witnesses,
        action_taken=data.action_taken
    )


@router.patch("/discipline/incidents/{incident_id}/resolve")
async def update_incident_resolution(
    school_id: str,
    incident_id: str,
    data: IncidentUpdate
):
    """Update incident with resolution"""
    service = get_discipline_service(school_id)
    return service.update_incident_resolution(
        incident_id=incident_id,
        action_taken=data.action_taken,
        resolved=data.resolved
    )


@router.get("/discipline/student/{student_id}/incidents")
async def get_student_incidents(
    school_id: str,
    student_id: str,
    include_resolved: bool = True
):
    """Get all incidents for a student"""
    service = get_discipline_service(school_id)
    return {
        "success": True,
        "incidents": service.get_student_incidents(student_id, include_resolved)
    }


@router.get("/discipline/incidents/unresolved")
async def get_unresolved_incidents(school_id: str):
    """Get all unresolved incidents"""
    service = get_discipline_service(school_id)
    return {
        "success": True,
        "unresolved_incidents": service.get_unresolved_incidents()
    }


# ============================================================================
# SUSPENSIONS
# ============================================================================

@router.post("/discipline/suspensions/create")
async def create_suspension(school_id: str, data: SuspensionCreate):
    """Create suspension record"""
    service = get_discipline_service(school_id)
    return service.create_suspension(
        student_id=data.student_id,
        reason=data.reason,
        start_date=data.start_date,
        end_date=data.end_date,
        suspended_by=data.suspended_by,
        related_incident_id=data.related_incident_id
    )


@router.patch("/discipline/suspensions/{suspension_id}/end")
async def end_suspension(
    school_id: str,
    suspension_id: str,
    notes: Optional[str] = None
):
    """Mark suspension as completed"""
    service = get_discipline_service(school_id)
    return service.end_suspension(suspension_id, notes)


@router.get("/discipline/suspensions/active")
async def get_active_suspensions(school_id: str):
    """Get all active suspensions"""
    service = get_discipline_service(school_id)
    return {
        "success": True,
        "active_suspensions": service.get_active_suspensions()
    }


@router.get("/discipline/student/{student_id}/suspensions")
async def get_student_suspensions(school_id: str, student_id: str):
    """Get suspension history for a student"""
    service = get_discipline_service(school_id)
    return {
        "success": True,
        "suspensions": service.get_student_suspensions(student_id)
    }


# ============================================================================
# ANALYTICS & REPORTS
# ============================================================================

@router.get("/discipline/student/{student_id}/summary")
async def get_behavior_summary(school_id: str, student_id: str):
    """Get behavior summary for a student"""
    service = get_discipline_service(school_id)
    return service.get_behavior_summary(student_id)


@router.get("/discipline/statistics")
async def get_school_statistics(school_id: str):
    """Get discipline statistics for the school"""
    service = get_discipline_service(school_id)
    return service.get_school_discipline_statistics()


@router.get("/discipline/students-at-risk")
async def get_students_at_risk(school_id: str):
    """Get students at risk (for intervention programs)"""
    service = get_discipline_service(school_id)
    return {
        "success": True,
        "students_at_risk": service.get_students_at_risk()
    }
