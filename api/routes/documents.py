"""
Documents API - Photos, IDs, Pass-Out Slips, Report Cards
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import Response
from api.services.photo import get_photo_service
from api.services.id_card_generator import get_id_card_generator
from api.services.passout_generator import get_passout_generator
from api.services.report_card_generator import get_report_card_generator
from api.core.auth import get_current_user

router = APIRouter(prefix="/api/documents", tags=["Documents \u0026 Photos"])

# ============ PHOTO UPLOAD ============

@router.post("/photos/upload")
async def upload_student_photo(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Upload student/staff photo
    Auto-processes into passport photo and thumbnail
    """
    photo_service = get_photo_service()
    
    # Read file
    image_data = await file.read()
    
    # Validate
    photo_service.validate_photo(image_data)
    
    # Process
    passport_photo, thumbnail = photo_service.process_passport_photo(image_data)
    
    # In production, save to R2/storage here
    # For now, return base64
    import base64
    
    return {
        "success": True,
        "passport_photo": base64.b64encode(passport_photo).decode(),
        "thumbnail": base64.b64encode(thumbnail).decode(),
        "message": "Photo processed successfully"
    }

# ============ ID CARDS ============

class StudentIDRequest(BaseModel):
    student_name: str
    student_id: str
    class_name: str
    school_name: str
    photo_base64: Optional[str] = None
    valid_until: Optional[str] = None

class StaffIDRequest(BaseModel):
    staff_name: str
    staff_id: str
    position: str
    department: str
    school_name: str
    photo_base64: Optional[str] = None
    valid_until: Optional[str] = None

@router.post("/id-cards/student")
async def generate_student_id_card(
    request: StudentIDRequest,
    current_user = Depends(get_current_user)
):
    """Generate student ID card (high-quality, printable)"""
    generator = get_id_card_generator()
    
    # Decode photo if provided
    photo_bytes = None
    if request.photo_base64:
        import base64
        photo_bytes = base64.b64decode(request.photo_base64)
    
    # Generate ID card
    id_card_bytes = generator.generate_student_id(
        student_name=request.student_name,
        student_id=request.student_id,
        class_name=request.class_name,
        school_name=request.school_name,
        photo_bytes=photo_bytes,
        valid_until=request.valid_until
    )
    
    # Return as PNG image (300 DPI, print-ready)
    return Response(
        content=id_card_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=student_id_{request.student_id}.png"
        }
    )

@router.post("/id-cards/staff")
async def generate_staff_id_card(
    request: StaffIDRequest,
    current_user = Depends(get_current_user)
):
    """Generate staff ID card (high-quality, printable)"""
    generator = get_id_card_generator()
    
    photo_bytes = None
    if request.photo_base64:
        import base64
        photo_bytes = base64.b64decode(request.photo_base64)
    
    id_card_bytes = generator.generate_staff_id(
        staff_name=request.staff_name,
        staff_id=request.staff_id,
        position=request.position,
        department=request.department,
        school_name=request.school_name,
        photo_bytes=photo_bytes,
        valid_until=request.valid_until
    )
    
    return Response(
        content=id_card_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=staff_id_{request.staff_id}.png"
        }
    )

# ============ PASS-OUT SLIPS ============

class PassOutRequest(BaseModel):
    student_name: str
    student_id: str
    class_name: str
    reason: str
    departure_time: str
    expected_return: Optional[str] = None
    authorized_by: str
    school_name: str
    photo_base64: Optional[str] = None
    parent_phone: Optional[str] = None

@router.post("/pass-out-slips/generate")
async def generate_pass_out_slip(
    request: PassOutRequest,
    current_user = Depends(get_current_user)
):
    """Generate pass-out slip (printable, A5 size)"""
    generator = get_passout_generator()
    
    photo_bytes = None
    if request.photo_base64:
        import base64
        photo_bytes = base64.b64decode(request.photo_base64)
    
    slip_bytes = generator.generate_pass_out_slip(
        student_name=request.student_name,
        student_id=request.student_id,
        class_name=request.class_name,
        reason=request.reason,
        departure_time=request.departure_time,
        expected_return=request.expected_return,
        authorized_by=request.authorized_by,
        school_name=request.school_name,
        photo_bytes=photo_bytes,
        parent_phone=request.parent_phone
    )
    
    return Response(
        content=slip_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=pass_out_{request.student_id}.png"
        }
    )

# ============ REPORT CARDS ============

class SubjectResult(BaseModel):
    name: str
    score: float
    grade: str
    remarks: str

class ReportCardRequest(BaseModel):
    student_name: str
    student_id: str
    class_name: str
    term: str
    year: str
    subjects: List[SubjectResult]
    school_name: str
    school_address: str
    photo_base64: Optional[str] = None
    class_teacher: Optional[str] = None

@router.post("/report-cards/generate")
async def generate_report_card(
    request: ReportCardRequest,
    current_user = Depends(get_current_user)
):
    """Generate report card with student photo (A4, print-ready)"""
    generator = get_report_card_generator()
    
    photo_bytes = None
    if request.photo_base64:
        import base64
        photo_bytes = base64.b64decode(request.photo_base64)
    
    # Convert subjects to dict
    subjects_dict = [s.dict() for s in request.subjects]
    
    report_bytes = generator.generate_report_card(
        student_name=request.student_name,
        student_id=request.student_id,
        class_name=request.class_name,
        term=request.term,
        year=request.year,
        subjects=subjects_dict,
        school_name=request.school_name,
        school_address=request.school_address,
        photo_bytes=photo_bytes,
        class_teacher=request.class_teacher
    )
    
    return Response(
        content=report_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"attachment; filename=report_card_{request.student_id}_{request.term}_{request.year}.png"
        }
    )

# ============ BATCH OPERATIONS ============

@router.post("/id-cards/batch/students")
async def batch_generate_student_ids(
    students: List[StudentIDRequest],
    current_user = Depends(get_current_user)
):
    """Generate ID cards for multiple students at once"""
    generator = get_id_card_generator()
    
    results = []
    for student in students:
        try:
            photo_bytes = None
            if student.photo_base64:
                import base64
                photo_bytes = base64.b64decode(student.photo_base64)
            
            id_bytes = generator.generate_student_id(
                student_name=student.student_name,
                student_id=student.student_id,
                class_name=student.class_name,
                school_name=student.school_name,
                photo_bytes=photo_bytes,
                valid_until=student.valid_until
            )
            
            results.append({
                "student_id": student.student_id,
                "success": True,
                "file_size": len(id_bytes)
            })
        except Exception as e:
            results.append({
                "student_id": student.student_id,
                "success": False,
                "error": str(e)
            })
    
    return {
        "total": len(students),
        "successful": sum(1 for r in results if r['success']),
        "failed": sum(1 for r in results if not r['success']),
        "results": results
    }
