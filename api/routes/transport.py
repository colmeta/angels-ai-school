"""
School Transport API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from api.services.transport import get_transport_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class RouteCreate(BaseModel):
    route_name: str
    route_code: str
    driver_name: str
    driver_phone: str
    vehicle_number: str
    vehicle_capacity: int
    pickup_time: str
    dropoff_time: str
    stops: List[Dict[str, str]]  # [{name: "Stop 1", arrival_time: "07:00"}]


class StudentAssignment(BaseModel):
    student_id: str
    route_id: str
    stop_name: str
    monthly_fee: float


class RouteNotification(BaseModel):
    route_id: str
    message: str


# ============================================================================
# ROUTES MANAGEMENT
# ============================================================================

@router.post("/transport/routes/create")
async def create_route(school_id: str, data: RouteCreate):
    """
    Create transport route
    
    Example:
    {
      "route_name": "Ntinda Route",
      "route_code": "R01",
      "driver_name": "John Ssemakula",
      "driver_phone": "+256700123456",
      "vehicle_number": "UAG 123A",
      "vehicle_capacity": 30,
      "pickup_time": "06:30",
      "dropoff_time": "15:00",
      "stops": [
        {"name": "Ntinda", "arrival_time": "06:30"},
        {"name": "Bukoto", "arrival_time": "06:45"}
      ]
    }
    """
    service = get_transport_service(school_id)
    return service.create_route(
        route_name=data.route_name,
        route_code=data.route_code,
        driver_name=data.driver_name,
        driver_phone=data.driver_phone,
        vehicle_number=data.vehicle_number,
        vehicle_capacity=data.vehicle_capacity,
        pickup_time=data.pickup_time,
        dropoff_time=data.dropoff_time,
        stops=data.stops
    )


@router.get("/transport/routes/list")
async def get_routes(school_id: str, is_active: bool = True):
    """Get all transport routes"""
    service = get_transport_service(school_id)
    return {
        "success": True,
        "routes": service.get_routes(is_active=is_active)
    }


@router.patch("/transport/routes/{route_id}")
async def update_route(school_id: str, route_id: str, updates: Dict[str, Any]):
    """Update route details"""
    service = get_transport_service(school_id)
    return service.update_route(route_id, updates)


# ============================================================================
# STUDENT ASSIGNMENTS
# ============================================================================

@router.post("/transport/assign-student")
async def assign_student(school_id: str, data: StudentAssignment):
    """Assign student to transport route"""
    service = get_transport_service(school_id)
    return service.assign_student_to_route(
        student_id=data.student_id,
        route_id=data.route_id,
        stop_name=data.stop_name,
        monthly_fee=data.monthly_fee
    )


@router.get("/transport/routes/{route_id}/students")
async def get_students_on_route(school_id: str, route_id: str):
    """Get all students on a specific route"""
    service = get_transport_service(school_id)
    return {
        "success": True,
        "students": service.get_students_on_route(route_id)
    }


@router.get("/transport/student/{student_id}")
async def get_student_transport_info(school_id: str, student_id: str):
    """Get transport info for a student"""
    service = get_transport_service(school_id)
    info = service.get_student_transport_info(student_id)
    
    if not info:
        return {"success": False, "error": "Student not assigned to transport"}
    
    return {"success": True, "transport_info": info}


@router.delete("/transport/student/{student_id}")
async def remove_student_from_transport(school_id: str, student_id: str):
    """Remove student from transport"""
    service = get_transport_service(school_id)
    return service.remove_student_from_transport(student_id)


# ============================================================================
# SCHEDULES & NOTIFICATIONS
# ============================================================================

@router.get("/transport/schedule/daily")
async def get_daily_schedule(school_id: str, date: str):
    """Get daily transport schedule"""
    service = get_transport_service(school_id)
    return {
        "success": True,
        "date": date,
        "schedule": service.get_daily_schedule(date)
    }


@router.post("/transport/notify-parents")
async def notify_parents_on_route(school_id: str, data: RouteNotification):
    """
    Send notification to all parents on a route
    
    Example:
    {
      "route_id": "abc",
      "message": "Bus delayed by 15 minutes due to traffic"
    }
    """
    service = get_transport_service(school_id)
    return service.bulk_notify_parents(data.route_id, data.message)


# ============================================================================
# ANALYTICS
# ============================================================================

@router.get("/transport/analytics/capacity")
async def get_capacity_report(school_id: str):
    """Get route capacity utilization report"""
    service = get_transport_service(school_id)
    return {
        "success": True,
        "capacity_report": service.get_route_capacity_report()
    }


@router.get("/transport/analytics/revenue")
async def get_monthly_revenue(school_id: str, month: str):
    """Get expected transport revenue for a month"""
    service = get_transport_service(school_id)
    return service.get_monthly_transport_revenue(month)
