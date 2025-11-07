"""Student Management Endpoints"""
from fastapi import APIRouter, HTTPException

from api.models.schemas import StudentRegistrationRequest
from api.services.executive import ExecutiveAssistant

router = APIRouter()


@router.post("/register")
async def register_student(data: StudentRegistrationRequest):
    try:
        assistant = ExecutiveAssistant(data.school_id)
        result = assistant.process_registration(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/dashboard/{school_id}")
async def get_dashboard(school_id: str):
    try:
        assistant = ExecutiveAssistant(school_id)
        return assistant.get_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
