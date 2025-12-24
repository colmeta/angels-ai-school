"""
Dynamic Attendance Router
Handles batch uploads from the Frontend AI Worker
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from api.core.auth import get_current_user
from api.services.attendance import get_attendance_service

router = APIRouter(prefix="/api/attendance", tags=["Attendance (Dynamic)"])

class AttendanceRecord(BaseModel):
    student_id: str
    class_name: str
    status: str # present, absent, etc
    mode: str # photo, voice, text, manual
    date: Optional[date] = None
    notes: Optional[str] = None
    
    # Subject specific
    subject: Optional[str] = None
    teacher_id: Optional[str] = None
    
    # Exam specific
    exam_name: Optional[str] = None
    booklet_number: Optional[str] = None
    supervisor_id: Optional[str] = None

class BatchAttendanceRequest(BaseModel):
    type: str # 'subject' or 'exam'
    records: List[AttendanceRecord]

@router.post("/batch")
async def submit_batch_attendance(
    payload: BatchAttendanceRequest,
    current_user = Depends(get_current_user)
):
    """
    Receive structured attendance data from Frontend AI Worker
    Supports Subject and Exam attendance
    """
    service = get_attendance_service(current_user['school_id'])
    
    # Convert Pydantic models to dicts
    records = [r.dict() for r in payload.records]
    
    if payload.type == 'subject':
        result = service.record_subject_attendance_batch(records)
    elif payload.type == 'exam':
        result = service.record_exam_attendance_batch(records)
    else:
        raise HTTPException(status_code=400, detail="Invalid attendance type")
        
    return result
