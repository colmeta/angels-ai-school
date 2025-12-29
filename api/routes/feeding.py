"""
School Feeding API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from api.services.feeding import get_feeding_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class MealMenuCreate(BaseModel):
    meal_type: str  # breakfast, lunch, dinner, snack
    menu_date: str
    items: List[str]
    description: Optional[str] = None
    allergen_info: Optional[str] = None


class MealAttendanceRecord(BaseModel):
    student_id: str
    meal_type: str
    meal_date: str
    attended: bool = True


class BulkMealAttendance(BaseModel):
    meal_type: str
    meal_date: str
    student_ids: List[str]


# ============================================================================
# MEAL MENU
# ============================================================================

@router.post("/feeding/menu/create")
async def create_meal_menu(school_id: str, data: MealMenuCreate):
    """
    Create meal menu
    
    Example:
    {
      "meal_type": "lunch",
      "menu_date": "2025-02-15",
      "items": ["Posho", "Beans", "Cabbage"],
      "description": "Traditional Ugandan lunch",
      "allergen_info": "Contains gluten"
    }
    """
    service = get_feeding_service(school_id)
    return service.create_meal_menu(
        meal_type=data.meal_type,
        menu_date=data.menu_date,
        items=data.items,
        description=data.description,
        allergen_info=data.allergen_info
    )


@router.get("/feeding/menu/date/{menu_date}")
async def get_menu_for_date(school_id: str, menu_date: str):
    """Get all meals for a specific date"""
    service = get_feeding_service(school_id)
    return {
        "success": True,
        "menu": service.get_menu_for_date(menu_date)
    }


@router.get("/feeding/menu/weekly")
async def get_weekly_menu(school_id: str, start_date: str):
    """Get menu for a week"""
    service = get_feeding_service(school_id)
    return service.get_weekly_menu(start_date)


# ============================================================================
# MEAL ATTENDANCE
# ============================================================================

@router.post("/feeding/attendance/record")
async def record_meal_attendance(school_id: str, data: MealAttendanceRecord):
    """Record single student meal attendance"""
    service = get_feeding_service(school_id)
    return service.record_meal_attendance(
        student_id=data.student_id,
        meal_type=data.meal_type,
        meal_date=data.meal_date,
        attended=data.attended
    )


@router.post("/feeding/attendance/bulk")
async def bulk_record_attendance(school_id: str, data: BulkMealAttendance):
    """
    Record meal attendance for multiple students
    
    Example: Take photo of students eating lunch, AI extracts names, bulk record
    """
    service = get_feeding_service(school_id)
    return service.bulk_record_meal_attendance(
        meal_type=data.meal_type,
        meal_date=data.meal_date,
        student_ids=data.student_ids
    )


@router.get("/feeding/attendance/date/{meal_date}")
async def get_attendance_for_date(
    school_id: str,
    meal_date: str,
    meal_type: str
):
    """Get meal attendance for a specific date and meal"""
    service = get_feeding_service(school_id)
    return {
        "success": True,
        "attendance": service.get_meal_attendance_for_date(meal_date, meal_type)
    }


@router.get("/feeding/student/{student_id}/history")
async def get_student_meal_history(
    school_id: str,
    student_id: str,
    start_date: str,
    end_date: str
):
    """Get meal history for a student"""
    service = get_feeding_service(school_id)
    return {
        "success": True,
        "history": service.get_student_meal_history(student_id, start_date, end_date)
    }


# ============================================================================
# ANALYTICS
# ============================================================================

@router.get("/feeding/analytics/daily/{meal_date}")
async def get_daily_meal_count(school_id: str, meal_date: str):
    """Get meal count for a specific date"""
    service = get_feeding_service(school_id)
    return service.get_daily_meal_count(meal_date)


@router.get("/feeding/analytics/statistics")
async def get_feeding_statistics(
    school_id: str,
    start_date: str,
    end_date: str
):
    """Get feeding statistics for a period"""
    service = get_feeding_service(school_id)
    return service.get_feeding_statistics(start_date, end_date)


@router.get("/feeding/welfare/not-eating")
async def get_students_not_eating(school_id: str, days: int = 3):
    """Get students who haven't eaten in X days (welfare check)"""
    service = get_feeding_service(school_id)
    return {
        "success": True,
        "students_not_eating": service.get_students_not_eating(days)
    }
