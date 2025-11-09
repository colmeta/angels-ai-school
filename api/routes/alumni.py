"""
Alumni Tracking API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from api.services.alumni import get_alumni_service


router = APIRouter()


class AlumniRegister(BaseModel):
    first_name: str
    last_name: str
    graduation_year: int
    graduation_class: str
    email: Optional[str] = None
    phone: Optional[str] = None
    current_occupation: Optional[str] = None
    employer: Optional[str] = None
    university_attended: Optional[str] = None
    degree_obtained: Optional[str] = None


@router.post("/alumni/register")
async def register_alumni(school_id: str, data: AlumniRegister):
    """Register an alumnus"""
    service = get_alumni_service(school_id)
    return service.register_alumni(
        first_name=data.first_name,
        last_name=data.last_name,
        graduation_year=data.graduation_year,
        graduation_class=data.graduation_class,
        email=data.email,
        phone=data.phone,
        current_occupation=data.current_occupation,
        employer=data.employer,
        university_attended=data.university_attended,
        degree_obtained=data.degree_obtained
    )


@router.patch("/alumni/{alumni_id}")
async def update_alumni(school_id: str, alumni_id: str, updates: Dict[str, Any]):
    """Update alumni information"""
    service = get_alumni_service(school_id)
    return service.update_alumni_info(alumni_id, updates)


@router.get("/alumni/search")
async def search_alumni(
    school_id: str,
    graduation_year: Optional[int] = None,
    occupation: Optional[str] = None,
    university: Optional[str] = None
):
    """Search alumni"""
    service = get_alumni_service(school_id)
    return {
        "success": True,
        "alumni": service.search_alumni(graduation_year, occupation, university)
    }


@router.get("/alumni/statistics")
async def get_statistics(school_id: str):
    """Get alumni statistics"""
    service = get_alumni_service(school_id)
    return service.get_alumni_statistics()
