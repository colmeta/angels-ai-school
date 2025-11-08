"""
Homework Tracking API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from api.services.homework import get_homework_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class AssignmentCreate(BaseModel):
    teacher_id: str
    subject: str
    class_name: str
    title: str
    description: str
    assigned_date: str
    due_date: str
    total_marks: int = 100


class HomeworkSubmit(BaseModel):
    assignment_id: str
    student_id: str
    submission_text: Optional[str] = None
    attachment_url: Optional[str] = None


class HomeworkGrade(BaseModel):
    marks_obtained: int
    feedback: Optional[str] = None


# ============================================================================
# HOMEWORK ASSIGNMENTS
# ============================================================================

@router.post("/homework/assignments/create")
async def create_assignment(school_id: str, data: AssignmentCreate):
    """Create homework assignment"""
    service = get_homework_service(school_id)
    return service.create_assignment(
        teacher_id=data.teacher_id,
        subject=data.subject,
        class_name=data.class_name,
        title=data.title,
        description=data.description,
        assigned_date=data.assigned_date,
        due_date=data.due_date,
        total_marks=data.total_marks
    )


@router.get("/homework/assignments/class/{class_name}")
async def get_assignments_for_class(
    school_id: str,
    class_name: str,
    subject: Optional[str] = None,
    include_past: bool = False
):
    """Get all assignments for a class"""
    service = get_homework_service(school_id)
    return {
        "success": True,
        "assignments": service.get_assignments_for_class(class_name, subject, include_past)
    }


@router.get("/homework/assignments/{assignment_id}")
async def get_assignment(school_id: str, assignment_id: str):
    """Get assignment details"""
    service = get_homework_service(school_id)
    assignment = service.get_assignment_by_id(assignment_id)
    
    if not assignment:
        return {"success": False, "error": "Assignment not found"}
    
    return {"success": True, "assignment": assignment}


# ============================================================================
# HOMEWORK SUBMISSIONS
# ============================================================================

@router.post("/homework/submit")
async def submit_homework(school_id: str, data: HomeworkSubmit):
    """Student submits homework"""
    service = get_homework_service(school_id)
    return service.submit_homework(
        assignment_id=data.assignment_id,
        student_id=data.student_id,
        submission_text=data.submission_text,
        attachment_url=data.attachment_url
    )


@router.patch("/homework/submissions/{submission_id}/grade")
async def grade_submission(school_id: str, submission_id: str, data: HomeworkGrade):
    """Teacher grades homework submission"""
    service = get_homework_service(school_id)
    return service.grade_submission(
        submission_id=submission_id,
        marks_obtained=data.marks_obtained,
        feedback=data.feedback
    )


@router.get("/homework/assignments/{assignment_id}/submissions")
async def get_submissions(school_id: str, assignment_id: str):
    """Get all submissions for an assignment"""
    service = get_homework_service(school_id)
    return {
        "success": True,
        "submissions": service.get_submissions_for_assignment(assignment_id)
    }


@router.get("/homework/student/{student_id}/submissions")
async def get_student_submissions(
    school_id: str,
    student_id: str,
    include_graded: bool = True
):
    """Get all submissions for a student"""
    service = get_homework_service(school_id)
    return {
        "success": True,
        "submissions": service.get_student_submissions(student_id, include_graded)
    }


@router.get("/homework/assignments/{assignment_id}/pending")
async def get_pending_submissions(school_id: str, assignment_id: str):
    """Get students who submitted but not yet graded"""
    service = get_homework_service(school_id)
    return {
        "success": True,
        "pending_submissions": service.get_pending_submissions(assignment_id)
    }


@router.get("/homework/assignments/{assignment_id}/missing")
async def get_missing_submissions(school_id: str, assignment_id: str):
    """Get students who haven't submitted"""
    service = get_homework_service(school_id)
    return {
        "success": True,
        "missing_submissions": service.get_missing_submissions(assignment_id)
    }


# ============================================================================
# ANALYTICS & REPORTS
# ============================================================================

@router.get("/homework/analytics/completion-rate")
async def get_completion_rate(
    school_id: str,
    class_name: str,
    subject: Optional[str] = None
):
    """Get homework completion rate for a class"""
    service = get_homework_service(school_id)
    return service.get_homework_completion_rate(class_name, subject)


@router.get("/homework/student/{student_id}/performance")
async def get_student_performance(school_id: str, student_id: str):
    """Get homework performance for a student"""
    service = get_homework_service(school_id)
    return service.get_student_homework_performance(student_id)
