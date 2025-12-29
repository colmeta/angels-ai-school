from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from api.services.support import SupportService


class IncidentPayload(BaseModel):
    category: str
    description: str
    severity: str = Field(..., description="low/medium/high/critical")
    reported_by: str
    status: Optional[str] = "open"
    occurred_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class InventoryAdjustment(BaseModel):
    item_name: str
    change_quantity: float
    unit: Optional[str] = None
    reason: str
    recorded_by: str
    metadata: Optional[Dict[str, Any]] = None


class HealthVisitPayload(BaseModel):
    student_name: str
    grade: Optional[str] = None
    symptoms: str
    action_taken: str
    guardian_contacted: Optional[str] = None
    recorded_by: str
    metadata: Optional[Dict[str, Any]] = None


class LibraryTransactionPayload(BaseModel):
    student_name: str
    class_name: Optional[str] = None
    book_title: str
    action: str = Field(..., description="borrow or return")
    due_date: Optional[str] = None
    recorded_by: str
    metadata: Optional[Dict[str, Any]] = None


class TransportEventPayload(BaseModel):
    route_name: str
    vehicle: Optional[str] = None
    status: str = Field(..., description="departed/arrived/delayed/cancelled")
    notes: Optional[str] = None
    recorded_by: str
    event_time: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


router = APIRouter(prefix="/support", tags=["Support Operations"])


def _service(school_id: str) -> SupportService:
    return SupportService(school_id)


@router.post("/{school_id}/incidents")
def create_incident(school_id: str, payload: IncidentPayload):
    try:
        service = _service(school_id)
        return service.log_incident(**payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{school_id}/incidents")
def get_incidents(
    school_id: str,
    limit: int = Query(50, ge=1, le=200),
):
    try:
        service = _service(school_id)
        return {"success": True, "incidents": service.list_incidents(limit=limit)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{school_id}/inventory/adjust")
def adjust_inventory(school_id: str, payload: InventoryAdjustment):
    try:
        service = _service(school_id)
        return service.adjust_inventory(**payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{school_id}/inventory")
def inventory_snapshot(school_id: str):
    try:
        service = _service(school_id)
        snapshot = service.inventory_snapshot()
        return {"success": True, **snapshot}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{school_id}/health")
def record_health_visit(school_id: str, payload: HealthVisitPayload):
    try:
        service = _service(school_id)
        return service.record_health_visit(**payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{school_id}/health")
def list_health_visits(school_id: str, limit: int = Query(50, ge=1, le=200)):
    try:
        service = _service(school_id)
        return {"success": True, "visits": service.list_health_visits(limit=limit)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{school_id}/library")
def record_library_transaction(school_id: str, payload: LibraryTransactionPayload):
    try:
        service = _service(school_id)
        return service.record_library_transaction(**payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{school_id}/library")
def list_library_transactions(school_id: str, limit: int = Query(50, ge=1, le=200)):
    try:
        service = _service(school_id)
        return {"success": True, "transactions": service.list_library_transactions(limit=limit)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{school_id}/transport")
def record_transport_event(school_id: str, payload: TransportEventPayload):
    try:
        service = _service(school_id)
        return service.record_transport_event(**payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{school_id}/transport")
def list_transport_events(school_id: str, limit: int = Query(50, ge=1, le=200)):
    try:
        service = _service(school_id)
        return {"success": True, "events": service.list_transport_events(limit=limit)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{school_id}/report")
def support_report(school_id: str):
    try:
        service = _service(school_id)
        return service.generate_support_report()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
