"""
Government Reporting API Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from api.services.government_reporting import get_government_reporting_service


router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ReportSave(BaseModel):
    report_type: str
    report_year: int
    report_data: Dict[str, Any]
    submitted_by: str


# ============================================================================
# REPORT GENERATION
# ============================================================================

@router.get("/government/reports/census")
async def generate_census(school_id: str, year: int):
    """
    Generate annual school census
    
    Example: /government/reports/census?school_id=abc&year=2025
    """
    service = get_government_reporting_service(school_id)
    return service.generate_annual_census(year)


@router.get("/government/reports/enrollment")
async def generate_enrollment_report(
    school_id: str,
    start_date: str,
    end_date: str
):
    """Generate enrollment report for a period"""
    service = get_government_reporting_service(school_id)
    return service.generate_enrollment_report(start_date, end_date)


@router.get("/government/reports/teachers")
async def generate_teacher_report(school_id: str):
    """Generate teacher data report"""
    service = get_government_reporting_service(school_id)
    return service.generate_teacher_data_report()


@router.get("/government/reports/infrastructure")
async def generate_infrastructure_report(school_id: str):
    """Generate infrastructure and facilities report"""
    service = get_government_reporting_service(school_id)
    return service.generate_infrastructure_report()


@router.get("/government/reports/financial")
async def generate_financial_report(
    school_id: str,
    start_date: str,
    end_date: str
):
    """Generate financial summary report"""
    service = get_government_reporting_service(school_id)
    return service.generate_financial_summary_report(start_date, end_date)


# ============================================================================
# REPORT STORAGE & SUBMISSION
# ============================================================================

@router.post("/government/reports/save")
async def save_report(school_id: str, data: ReportSave):
    """Save generated report to database"""
    service = get_government_reporting_service(school_id)
    return service.save_report(
        report_type=data.report_type,
        report_year=data.report_year,
        report_data=data.report_data,
        submitted_by=data.submitted_by
    )


@router.patch("/government/reports/{report_id}/submit")
async def submit_report(school_id: str, report_id: str, submission_date: str):
    """Mark report as submitted to government"""
    service = get_government_reporting_service(school_id)
    return service.mark_report_submitted(report_id, submission_date)


@router.get("/government/reports/list")
async def get_reports(
    school_id: str,
    report_type: Optional[str] = None,
    year: Optional[int] = None
):
    """Get all reports"""
    service = get_government_reporting_service(school_id)
    return {
        "success": True,
        "reports": service.get_reports(report_type, year)
    }


@router.get("/government/reports/{report_id}")
async def get_report_by_id(school_id: str, report_id: str):
    """Get full report data"""
    service = get_government_reporting_service(school_id)
    report = service.get_report_by_id(report_id)
    
    if not report:
        return {"success": False, "error": "Report not found"}
    
    return {"success": True, "report": report}
