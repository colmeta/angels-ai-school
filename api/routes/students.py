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

@router.get("")
async def list_students(school_id: str = None, current_class: str = None, limit: int = 100):
    """List students with optional filters"""
    # Quick implementation for load testing - in real app should be in services/ops
    if not school_id:
         raise HTTPException(status_code=400, detail="school_id required")
         
    from api.services.database import get_db, StudentOperations, DatabaseManager
    # We use a fresh DB manager or get_db dependency if available. 
    # For now, quick raw query or via Ops if they support list.
    
    # Ops list support? Unknown. Let's use DatabaseManager pattern.
    db = DatabaseManager()
    
    query = "SELECT * FROM students WHERE school_id = %s"
    params = [school_id]
    
    if current_class:
        query += " AND class_name = %s"
        params.append(current_class)
        
    query += " LIMIT %s"
    params.append(limit)
    
    try:
        results = db.execute_query(query, tuple(params))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close_all_connections()
