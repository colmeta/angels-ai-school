"""Student Management Endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from services.executive import ExecutiveAssistant

router = APIRouter()

class StudentRegistration(BaseModel):
    school_id: str
    student: dict
    parents: list
    emergency: dict

@router.post("/register")
async def register_student(data: StudentRegistration):
    try:
        assistant = ExecutiveAssistant(data.school_id)
        result = assistant.process_registration(data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{school_id}")
async def get_dashboard(school_id: str):
    try:
        assistant = ExecutiveAssistant(school_id)
        return assistant.get_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
