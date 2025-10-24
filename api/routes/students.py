"""
Student Management Endpoints
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
from executive_assistant_service import ExecutiveAssistantService
from fastapi import APIRouter, HTTPException, Body

router = APIRouter()

class StudentRegistration(BaseModel):
    school_id: str
    student: dict
    parents: list
    emergency: dict

@router.post("/register")
async def register_student(data: StudentRegistration):
    """Register a new student"""
    try:
        service = ExecutiveAssistantService(data.school_id)
        result = service.process_student_registration(data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enrollment/{school_id}")
async def get_enrollment_stats(school_id: str, period: str = "week"):
    """Get enrollment statistics"""
    try:
        service = ExecutiveAssistantService(school_id)
        stats = service.get_enrollment_statistics(period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{school_id}")
async def get_executive_dashboard(school_id: str, report_type: str = "daily"):
    """Get executive dashboard data"""
    try:
        service = ExecutiveAssistantService(school_id)
        report = service.generate_executive_report(report_type)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
