"""
Boarding School API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from api.services.boarding import get_boarding_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class DormitoryCreate(BaseModel):
    name: str
    dormitory_type: str  # boys, girls, mixed
    capacity: int
    matron_name: Optional[str] = None
    matron_phone: Optional[str] = None


class BedsCreate(BaseModel):
    dormitory_id: str
    bed_count: int
    bed_prefix: str = "BED"


class BedAssignment(BaseModel):
    student_id: str
    bed_id: str


class BoardingItemsTracking(BaseModel):
    student_id: str
    items: List[Dict[str, Any]]  # [{name: "Mattress", quantity: 1, condition: "new"}]


class ExeatRequestCreate(BaseModel):
    student_id: str
    parent_id: str
    reason: str
    leave_date: str
    return_date: str


# ============================================================================
# DORMITORY MANAGEMENT
# ============================================================================

@router.post("/boarding/dormitories/create")
async def create_dormitory(school_id: str, data: DormitoryCreate):
    """Create a dormitory"""
    service = get_boarding_service(school_id)
    return service.create_dormitory(
        name=data.name,
        dormitory_type=data.dormitory_type,
        capacity=data.capacity,
        matron_name=data.matron_name,
        matron_phone=data.matron_phone
    )


@router.get("/boarding/dormitories/list")
async def get_dormitories(school_id: str):
    """Get all dormitories with occupancy"""
    service = get_boarding_service(school_id)
    return {
        "success": True,
        "dormitories": service.get_dormitories()
    }


@router.post("/boarding/beds/create")
async def create_beds(school_id: str, data: BedsCreate):
    """Create multiple beds in a dormitory"""
    service = get_boarding_service(school_id)
    return service.create_beds(
        dormitory_id=data.dormitory_id,
        bed_count=data.bed_count,
        bed_prefix=data.bed_prefix
    )


# ============================================================================
# BED ASSIGNMENTS
# ============================================================================

@router.post("/boarding/beds/assign")
async def assign_bed(school_id: str, data: BedAssignment):
    """Assign student to a bed"""
    service = get_boarding_service(school_id)
    return service.assign_bed(
        student_id=data.student_id,
        bed_id=data.bed_id
    )


@router.get("/boarding/student/{student_id}/bed")
async def get_student_bed(school_id: str, student_id: str):
    """Get bed assignment for a student"""
    service = get_boarding_service(school_id)
    bed_info = service.get_student_bed(student_id)
    
    if not bed_info:
        return {"success": False, "error": "No bed assigned"}
    
    return {"success": True, "bed_info": bed_info}


@router.delete("/boarding/beds/{bed_id}")
async def vacate_bed(school_id: str, bed_id: str):
    """Vacate a bed"""
    service = get_boarding_service(school_id)
    return service.vacate_bed(bed_id)


# ============================================================================
# BOARDING ITEMS TRACKING
# ============================================================================

@router.post("/boarding/items/track")
async def track_boarding_items(school_id: str, data: BoardingItemsTracking):
    """
    Track boarding items brought by student
    
    Example:
    {
      "student_id": "abc",
      "items": [
        {"name": "Mattress", "quantity": 1, "condition": "new"},
        {"name": "Bedsheets", "quantity": 2, "condition": "good"},
        {"name": "Blankets", "quantity": 2, "condition": "good"}
      ]
    }
    """
    service = get_boarding_service(school_id)
    return service.track_boarding_items(
        student_id=data.student_id,
        items=data.items
    )


@router.get("/boarding/student/{student_id}/items")
async def get_student_items(school_id: str, student_id: str):
    """Get all boarding items for a student"""
    service = get_boarding_service(school_id)
    return {
        "success": True,
        "items": service.get_student_boarding_items(student_id)
    }


@router.patch("/boarding/items/{item_id}/return")
async def return_item(school_id: str, item_id: str, return_condition: str):
    """Mark boarding item as returned"""
    service = get_boarding_service(school_id)
    return service.return_boarding_item(item_id, return_condition)


# ============================================================================
# EXEAT REQUESTS
# ============================================================================

@router.post("/boarding/exeat/create")
async def create_exeat_request(school_id: str, data: ExeatRequestCreate):
    """Create exeat request (permission to leave boarding)"""
    service = get_boarding_service(school_id)
    return service.create_exeat_request(
        student_id=data.student_id,
        parent_id=data.parent_id,
        reason=data.reason,
        leave_date=data.leave_date,
        return_date=data.return_date
    )


@router.patch("/boarding/exeat/{exeat_id}/approve")
async def approve_exeat(school_id: str, exeat_id: str, approved_by: str):
    """Approve exeat request"""
    service = get_boarding_service(school_id)
    return service.approve_exeat(exeat_id, approved_by)


@router.patch("/boarding/exeat/{exeat_id}/depart")
async def record_departure(school_id: str, exeat_id: str):
    """Record student departure"""
    service = get_boarding_service(school_id)
    return service.record_student_departure(exeat_id)


@router.patch("/boarding/exeat/{exeat_id}/return")
async def record_return(school_id: str, exeat_id: str):
    """Record student return"""
    service = get_boarding_service(school_id)
    return service.record_student_return(exeat_id)


@router.get("/boarding/exeat/pending")
async def get_pending_exeats(school_id: str):
    """Get all pending exeat requests"""
    service = get_boarding_service(school_id)
    return {
        "success": True,
        "pending_exeats": service.get_pending_exeats()
    }


@router.get("/boarding/exeat/currently-away")
async def get_students_away(school_id: str):
    """Get all students currently on exeat"""
    service = get_boarding_service(school_id)
    return {
        "success": True,
        "students_away": service.get_students_currently_away()
    }
