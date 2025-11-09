"""
Health Records & Vaccination API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from api.services.health import get_health_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class HealthRecordCreate(BaseModel):
    student_id: str
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_notes: Optional[str] = None


class VaccinationRecord(BaseModel):
    student_id: str
    vaccine_name: str
    administered_by: str
    administered_date: str
    next_dose_date: Optional[str] = None
    notes: Optional[str] = None


class SickBayVisit(BaseModel):
    student_id: str
    symptoms: str
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    attended_by: Optional[str] = None
    parent_notified: bool = False


# ============================================================================
# HEALTH RECORDS
# ============================================================================

@router.post("/health/records/create")
async def create_health_record(school_id: str, data: HealthRecordCreate):
    """Create or update health record"""
    service = get_health_service(school_id)
    return service.create_health_record(
        student_id=data.student_id,
        blood_type=data.blood_type,
        allergies=data.allergies,
        chronic_conditions=data.chronic_conditions,
        emergency_contact_name=data.emergency_contact_name,
        emergency_contact_phone=data.emergency_contact_phone,
        medical_notes=data.medical_notes
    )


@router.get("/health/records/student/{student_id}")
async def get_student_health_record(school_id: str, student_id: str):
    """Get health record for a student"""
    service = get_health_service(school_id)
    record = service.get_student_health_record(student_id)
    
    if not record:
        return {"success": False, "error": "No health record found"}
    
    return {"success": True, "health_record": record}


# ============================================================================
# VACCINATIONS
# ============================================================================

@router.post("/health/vaccinations/record")
async def record_vaccination(school_id: str, data: VaccinationRecord):
    """Record vaccination for a student"""
    service = get_health_service(school_id)
    return service.record_vaccination(
        student_id=data.student_id,
        vaccine_name=data.vaccine_name,
        administered_by=data.administered_by,
        administered_date=data.administered_date,
        next_dose_date=data.next_dose_date,
        notes=data.notes
    )


@router.get("/health/vaccinations/student/{student_id}")
async def get_student_vaccinations(school_id: str, student_id: str):
    """Get all vaccinations for a student"""
    service = get_health_service(school_id)
    return {
        "success": True,
        "vaccinations": service.get_student_vaccinations(student_id)
    }


@router.get("/health/vaccinations/upcoming")
async def get_upcoming_vaccinations(school_id: str, days_ahead: int = 30):
    """Get students with upcoming vaccinations"""
    service = get_health_service(school_id)
    return {
        "success": True,
        "upcoming": service.get_upcoming_vaccinations(days_ahead)
    }


# ============================================================================
# SICK BAY
# ============================================================================

@router.post("/health/sick-bay/admit")
async def record_sick_bay_visit(school_id: str, data: SickBayVisit):
    """Record sick bay visit"""
    service = get_health_service(school_id)
    return service.record_sick_bay_visit(
        student_id=data.student_id,
        symptoms=data.symptoms,
        diagnosis=data.diagnosis,
        treatment=data.treatment,
        attended_by=data.attended_by,
        parent_notified=data.parent_notified
    )


@router.patch("/health/sick-bay/{visit_id}/discharge")
async def discharge_from_sick_bay(
    school_id: str,
    visit_id: str,
    discharge_notes: Optional[str] = None
):
    """Discharge student from sick bay"""
    service = get_health_service(school_id)
    return service.discharge_from_sick_bay(visit_id, discharge_notes)


@router.get("/health/sick-bay/current")
async def get_current_patients(school_id: str):
    """Get students currently in sick bay"""
    service = get_health_service(school_id)
    return {
        "success": True,
        "current_patients": service.get_sick_bay_current_patients()
    }


@router.get("/health/sick-bay/student/{student_id}/history")
async def get_student_sick_bay_history(school_id: str, student_id: str):
    """Get sick bay visit history for a student"""
    service = get_health_service(school_id)
    return {
        "success": True,
        "history": service.get_student_sick_bay_history(student_id)
    }


# ============================================================================
# ANALYTICS
# ============================================================================

@router.get("/health/summary")
async def get_health_summary(school_id: str):
    """Get health statistics for the school"""
    service = get_health_service(school_id)
    return service.get_health_summary()


@router.get("/health/allergies")
async def get_students_with_allergies(school_id: str):
    """Get all students with allergies"""
    service = get_health_service(school_id)
    return {
        "success": True,
        "students_with_allergies": service.get_students_with_allergies()
    }
