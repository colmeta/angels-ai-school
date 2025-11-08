"""
School Requirements Routes
API endpoints for managing supplies, trip fees, and other requirements
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List

from api.services.requirements import get_requirements_service

router = APIRouter(tags=["School Requirements"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class CreateRequirementRequest(BaseModel):
    name: str
    requirement_type: str  # supply, fee, both
    category_id: Optional[str] = None
    description: Optional[str] = None
    quantity_required: Optional[int] = None
    unit: Optional[str] = None
    amount_required: Optional[float] = None
    applies_to: str = 'all_students'
    target_class: Optional[str] = None
    due_date: Optional[str] = None
    term: Optional[str] = None
    is_mandatory: bool = True


class SubmitRequirementRequest(BaseModel):
    requirement_id: str
    student_id: str
    quantity_submitted: Optional[int] = None
    amount_paid: Optional[float] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    submission_date: Optional[str] = None
    condition: Optional[str] = 'new'
    notes: Optional[str] = None


class BulkSubmitRequest(BaseModel):
    requirement_id: str
    class_name: str
    quantity_submitted: Optional[int] = None
    amount_paid: Optional[float] = None
    exclude_students: Optional[List[str]] = None


# ============================================================================
# REQUIREMENT MANAGEMENT
# ============================================================================

@router.post("/requirements/create")
async def create_requirement(school_id: str, payload: CreateRequirementRequest):
    """
    Create a new school requirement
    
    Examples:
    - Toilet Paper: type=supply, quantity=2, unit=rolls
    - Trip to Museum: type=fee, amount=20000
    - Broom: type=supply, quantity=1, unit=pieces
    - Exam Fee: type=fee, amount=15000
    """
    try:
        service = get_requirements_service(school_id)
        result = service.create_requirement(
            name=payload.name,
            requirement_type=payload.requirement_type,
            category_id=payload.category_id,
            description=payload.description,
            quantity_required=payload.quantity_required,
            unit=payload.unit,
            amount_required=payload.amount_required,
            applies_to=payload.applies_to,
            target_class=payload.target_class,
            due_date=payload.due_date,
            term=payload.term,
            is_mandatory=payload.is_mandatory
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirements/list")
async def get_requirements(
    school_id: str,
    category_id: Optional[str] = None,
    requirement_type: Optional[str] = None,
    class_name: Optional[str] = None
):
    """
    Get all requirements for a school
    
    Filters:
    - category_id: Filter by category (Supplies, Trip Fees, etc.)
    - requirement_type: supply, fee, both
    - class_name: Get requirements for specific class
    """
    try:
        service = get_requirements_service(school_id)
        requirements = service.get_requirements(
            category_id=category_id,
            requirement_type=requirement_type,
            class_name=class_name
        )
        return {
            "school_id": school_id,
            "total": len(requirements),
            "requirements": requirements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirements/{requirement_id}/completion")
async def get_requirement_completion(school_id: str, requirement_id: str):
    """
    Get completion summary for a requirement
    
    Returns:
    - Total students
    - Submitted count
    - Pending count
    - Completion percentage
    - List of pending students
    """
    try:
        service = get_requirements_service(school_id)
        summary = service.get_requirement_completion_summary(requirement_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STUDENT SUBMISSIONS
# ============================================================================

@router.post("/requirements/submit")
async def submit_requirement(school_id: str, payload: SubmitRequirementRequest):
    """
    Record a student's submission
    
    Use cases:
    - Parent submits via app: "I brought 2 rolls of toilet paper"
    - Teacher manually enters: "John brought his broom today"
    - Admin bulk imports from photo/spreadsheet
    """
    try:
        service = get_requirements_service(school_id)
        result = service.submit_requirement(
            requirement_id=payload.requirement_id,
            student_id=payload.student_id,
            quantity_submitted=payload.quantity_submitted,
            amount_paid=payload.amount_paid,
            payment_method=payload.payment_method,
            payment_reference=payload.payment_reference,
            submission_date=payload.submission_date,
            condition=payload.condition,
            notes=payload.notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/requirements/submit-with-photo")
async def submit_with_photo(
    school_id: str = Form(...),
    requirement_id: str = Form(...),
    student_id: str = Form(...),
    quantity_submitted: Optional[int] = Form(None),
    amount_paid: Optional[float] = Form(None),
    file: UploadFile = File(...)
):
    """
    Submit requirement with photo proof
    
    Example: Take photo of toilet paper rolls brought by student
    """
    try:
        # TODO: Upload photo to storage (S3/Cloudinary)
        photo_url = f"https://storage.example.com/{file.filename}"
        
        service = get_requirements_service(school_id)
        result = service.submit_requirement(
            requirement_id=requirement_id,
            student_id=student_id,
            quantity_submitted=quantity_submitted,
            amount_paid=amount_paid,
            photo_url=photo_url
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/requirements/verify/{submission_id}")
async def verify_submission(school_id: str, submission_id: str, verified_by: Optional[str] = None):
    """
    Verify a submission (teacher/admin confirms item is acceptable)
    
    Example: Teacher checks toilet paper quality and approves
    """
    try:
        service = get_requirements_service(school_id)
        result = service.verify_submission(submission_id, verified_by)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirements/student/{student_id}/status")
async def get_student_requirements_status(
    school_id: str,
    student_id: str,
    status: Optional[str] = None
):
    """
    Get all requirements and their status for a student
    
    Status filters: submitted, pending, overdue
    
    Perfect for parent portal: "What does my child still need to bring?"
    """
    try:
        service = get_requirements_service(school_id)
        submissions = service.get_student_submissions(student_id, status)
        return {
            "student_id": student_id,
            "school_id": school_id,
            "requirements": submissions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirements/class/{class_name}/status")
async def get_class_requirements_status(
    school_id: str,
    class_name: str,
    requirement_id: Optional[str] = None
):
    """
    Get submission status for entire class
    
    Perfect for teacher: "Who in Class 5A hasn't brought toilet paper?"
    """
    try:
        service = get_requirements_service(school_id)
        submissions = service.get_class_submissions(class_name, requirement_id)
        return {
            "school_id": school_id,
            "class_name": class_name,
            "students": submissions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/requirements/bulk-submit")
async def bulk_submit_for_class(school_id: str, payload: BulkSubmitRequest):
    """
    Mark requirement as submitted for all students in a class
    
    Example: "Mark all Class 5A as having brought toilet paper"
    Useful when teacher verifies in bulk
    """
    try:
        service = get_requirements_service(school_id)
        result = service.bulk_submit_for_class(
            requirement_id=payload.requirement_id,
            class_name=payload.class_name,
            quantity_submitted=payload.quantity_submitted,
            amount_paid=payload.amount_paid,
            exclude_students=payload.exclude_students
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXAMPLES & DOCUMENTATION
# ============================================================================

@router.get("/requirements/examples")
async def get_requirements_examples():
    """Get examples of common school requirements"""
    return {
        "common_supplies": [
            {
                "name": "Toilet Paper",
                "type": "supply",
                "quantity": 2,
                "unit": "rolls",
                "description": "Soft toilet tissue, 2-ply"
            },
            {
                "name": "Broom",
                "type": "supply",
                "quantity": 1,
                "unit": "pieces",
                "description": "Hard broom for classroom cleaning"
            },
            {
                "name": "Soap",
                "type": "supply",
                "quantity": 2,
                "unit": "bars",
                "description": "Bathing soap or hand washing soap"
            },
            {
                "name": "Hand Sanitizer",
                "type": "supply",
                "quantity": 1,
                "unit": "bottles",
                "description": "500ml bottle, alcohol-based"
            },
            {
                "name": "Trash Bags",
                "type": "supply",
                "quantity": 5,
                "unit": "pieces",
                "description": "Large black trash bags"
            }
        ],
        "common_fees": [
            {
                "name": "Trip to National Museum",
                "type": "fee",
                "amount": 20000,
                "currency": "UGX",
                "description": "Transportation + entrance fee"
            },
            {
                "name": "End of Term Exams",
                "type": "fee",
                "amount": 15000,
                "currency": "UGX",
                "description": "Examination fees for Term 1"
            },
            {
                "name": "Sports Day",
                "type": "fee",
                "amount": 10000,
                "currency": "UGX",
                "description": "Sports uniform + refreshments"
            },
            {
                "name": "Science Fair Materials",
                "type": "fee",
                "amount": 25000,
                "currency": "UGX",
                "description": "Contribution for science project materials"
            }
        ],
        "usage_examples": {
            "create_supply_requirement": {
                "endpoint": "POST /api/requirements/create",
                "payload": {
                    "school_id": "school-123",
                    "name": "Toilet Paper",
                    "requirement_type": "supply",
                    "quantity_required": 2,
                    "unit": "rolls",
                    "applies_to": "all_students",
                    "due_date": "2025-02-01",
                    "term": "Term 1",
                    "is_mandatory": True
                }
            },
            "create_trip_fee": {
                "endpoint": "POST /api/requirements/create",
                "payload": {
                    "school_id": "school-123",
                    "name": "Trip to Zoo",
                    "requirement_type": "fee",
                    "amount_required": 20000,
                    "applies_to": "specific_class",
                    "target_class": "Class 5A",
                    "due_date": "2025-03-15"
                }
            },
            "parent_submits": {
                "endpoint": "POST /api/requirements/submit",
                "payload": {
                    "school_id": "school-123",
                    "requirement_id": "req-456",
                    "student_id": "student-789",
                    "quantity_submitted": 2,
                    "notes": "Brought 2 rolls as required"
                }
            },
            "teacher_verifies": {
                "endpoint": "POST /api/requirements/verify/{submission_id}",
                "result": "Submission marked as verified"
            },
            "check_class_status": {
                "endpoint": "GET /api/requirements/class/Class%205A/status",
                "result": "List of all students with their submission status"
            }
        }
    }
