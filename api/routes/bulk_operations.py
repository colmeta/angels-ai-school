"""
Bulk Operations Routes - Mass data operations API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from pydantic import BaseModel
from typing import Optional, List

from api.services.bulk_operations import get_bulk_service
from api.services.auth import AuthService

router = APIRouter(tags=["Bulk Operations"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class BulkAttendanceRequest(BaseModel):
    school_id: str
    class_name: str
    status: str = "present"
    date: Optional[str] = None
    exclude_students: Optional[List[str]] = None


class BulkAttendanceExceptRequest(BaseModel):
    school_id: str
    class_name: str
    absent_students: List[str]
    date: Optional[str] = None


class BulkMessageRequest(BaseModel):
    school_id: str
    recipient_type: str  # "all_parents", "all_teachers", "all_students", "class_parents"
    title: str
    message: str
    filters: Optional[dict] = None
    channels: Optional[List[str]] = None


# ============================================================================
# BULK ATTENDANCE
# ============================================================================

@router.post("/bulk/attendance/mark-class")
async def mark_class_attendance(
    payload: BulkAttendanceRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Mark attendance for entire class
    
    Examples:
    - Mark all Class 5A present
    - Mark all Primary 3 absent
    - Mark all Secondary 1A late
    """
    try:
        # Verify permissions (teachers, admin only)
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            auth = AuthService()
            try:
                token_data = auth.verify_token(token)
                role = token_data.get("role")
                if role not in ["teacher", "admin"]:
                    raise HTTPException(status_code=403, detail="Permission denied")
            except:
                pass
        
        bulk_service = get_bulk_service(payload.school_id)
        result = await bulk_service.mark_class_attendance(
            class_name=payload.class_name,
            status=payload.status,
            date_str=payload.date,
            exclude_students=payload.exclude_students
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/attendance/mark-except")
async def mark_all_except(
    payload: BulkAttendanceExceptRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Mark all students present except specified ones (marked absent)
    
    Example:
    {
      "class_name": "Class 5A",
      "absent_students": ["John", "Mary"]
    }
    → Marks everyone present except John and Mary
    """
    try:
        bulk_service = get_bulk_service(payload.school_id)
        result = await bulk_service.mark_all_present_except(
            class_name=payload.class_name,
            absent_students=payload.absent_students,
            date_str=payload.date
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BULK STUDENT IMPORT
# ============================================================================

@router.post("/bulk/students/import-csv")
async def import_students_csv(
    school_id: str,
    file: UploadFile = File(...),
    update_existing: bool = False,
    authorization: Optional[str] = Header(None)
):
    """
    Import students from CSV file
    
    CSV Format:
    first_name,last_name,date_of_birth,gender,class_name,admission_number
    John,Doe,2010-05-15,Male,Class 5A,2024001
    Mary,Smith,2011-03-20,Female,Class 5A,2024002
    """
    try:
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        bulk_service = get_bulk_service(school_id)
        result = await bulk_service.import_students_from_csv(
            csv_content=csv_content,
            update_existing=update_existing
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BULK GRADING
# ============================================================================

@router.post("/bulk/grades/import-csv")
async def import_grades_csv(
    school_id: str,
    assessment_name: str,
    subject: str,
    file: UploadFile = File(...),
    max_marks: float = 100,
    authorization: Optional[str] = Header(None)
):
    """
    Import grades from CSV
    
    CSV Format:
    admission_number,marks
    2024001,85
    2024002,92
    """
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        bulk_service = get_bulk_service(school_id)
        result = await bulk_service.import_grades_from_csv(
            csv_content=csv_content,
            assessment_name=assessment_name,
            subject=subject,
            max_marks=max_marks
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BULK MESSAGING
# ============================================================================

@router.post("/bulk/messages/send")
async def send_bulk_message(
    payload: BulkMessageRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Send message to multiple recipients
    
    Recipient Types:
    - "all_parents" - All parents in school
    - "all_teachers" - All teachers
    - "all_students" - All students
    - "class_parents" - Parents of specific class (provide class_name in filters)
    
    Example:
    {
      "recipient_type": "class_parents",
      "title": "Class Trip Tomorrow",
      "message": "Don't forget to send 10,000 UGX for the trip",
      "filters": {"class_name": "Class 5A"},
      "channels": ["app", "sms", "email"]
    }
    """
    try:
        bulk_service = get_bulk_service(payload.school_id)
        result = await bulk_service.send_bulk_message(
            recipient_type=payload.recipient_type,
            title=payload.title,
            message=payload.message,
            filters=payload.filters,
            channels=payload.channels
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BULK OPERATIONS EXAMPLES
# ============================================================================

@router.get("/bulk/examples")
async def get_bulk_examples():
    """Get examples of bulk operations"""
    return {
        "bulk_attendance": {
            "mark_entire_class": {
                "description": "Mark all students in a class present/absent/late",
                "endpoint": "POST /api/bulk/attendance/mark-class",
                "example": {
                    "school_id": "school-123",
                    "class_name": "Class 5A",
                    "status": "present"
                }
            },
            "mark_except": {
                "description": "Mark all present except specific students",
                "endpoint": "POST /api/bulk/attendance/mark-except",
                "example": {
                    "school_id": "school-123",
                    "class_name": "Class 5A",
                    "absent_students": ["John", "Mary"]
                }
            }
        },
        "bulk_students": {
            "import_csv": {
                "description": "Import 100+ students from CSV",
                "endpoint": "POST /api/bulk/students/import-csv",
                "csv_format": "first_name,last_name,date_of_birth,gender,class_name,admission_number"
            }
        },
        "bulk_grades": {
            "import_csv": {
                "description": "Import grades for all students",
                "endpoint": "POST /api/bulk/grades/import-csv",
                "csv_format": "admission_number,marks"
            }
        },
        "bulk_messaging": {
            "send_to_all": {
                "description": "Send message to all parents/teachers/students",
                "endpoint": "POST /api/bulk/messages/send",
                "recipient_types": [
                    "all_parents",
                    "all_teachers",
                    "all_students",
                    "class_parents"
                ]
            }
        },
        "natural_language_commands": {
            "examples": [
                "Mark all Class 5A as present",
                "Mark all Primary 3 as absent",
                "Send message to all parents: School closes early tomorrow",
                "Send message to Class 5A parents: Field trip on Friday"
            ],
            "note": "Use POST /api/command/execute for natural language commands"
        }
    }
