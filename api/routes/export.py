"""
Data Export Routes - CSV and PDF exports
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from api.services.export import get_export_service

router = APIRouter(tags=["Data Export"])


# ============================================================================
# CSV EXPORTS
# ============================================================================

@router.get("/export/students/csv")
async def export_students_csv(
    school_id: str,
    class_name: Optional[str] = None
):
    """
    Export students to CSV
    
    Query params:
    - school_id: School ID (required)
    - class_name: Filter by class (optional)
    """
    try:
        export_service = get_export_service(school_id)
        csv_data = export_service.export_students_csv(class_name)
        
        filename = f"students_{class_name or 'all'}_{export_service.db.execute_query('SELECT CURRENT_DATE', fetch=True)[0]['current_date']}.csv"
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/attendance/csv")
async def export_attendance_csv(
    school_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    class_name: Optional[str] = None
):
    """
    Export attendance records to CSV
    
    Query params:
    - school_id: School ID (required)
    - start_date: Start date (YYYY-MM-DD, optional)
    - end_date: End date (YYYY-MM-DD, optional)
    - class_name: Filter by class (optional)
    """
    try:
        export_service = get_export_service(school_id)
        csv_data = export_service.export_attendance_csv(start_date, end_date, class_name)
        
        filename = f"attendance_{start_date or 'all'}_{end_date or 'all'}.csv"
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/grades/csv")
async def export_grades_csv(
    school_id: str,
    assessment_name: Optional[str] = None,
    class_name: Optional[str] = None
):
    """
    Export grades to CSV
    
    Query params:
    - school_id: School ID (required)
    - assessment_name: Filter by assessment (optional)
    - class_name: Filter by class (optional)
    """
    try:
        export_service = get_export_service(school_id)
        csv_data = export_service.export_grades_csv(assessment_name, class_name)
        
        filename = f"grades_{assessment_name or 'all'}_{class_name or 'all'}.csv"
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/fees/csv")
async def export_fees_csv(
    school_id: str,
    status: Optional[str] = None
):
    """
    Export fee records to CSV
    
    Query params:
    - school_id: School ID (required)
    - status: Filter by status (paid/pending/overdue, optional)
    """
    try:
        export_service = get_export_service(school_id)
        csv_data = export_service.export_fees_csv(status)
        
        filename = f"fees_{status or 'all'}.csv"
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PDF EXPORTS
# ============================================================================

@router.get("/export/report-card/{student_id}/pdf")
async def export_report_card_pdf(
    student_id: str,
    school_id: str
):
    """
    Generate PDF report card for student
    
    Path params:
    - student_id: Student ID
    
    Query params:
    - school_id: School ID
    """
    try:
        export_service = get_export_service(school_id)
        pdf_data = export_service.export_report_card_pdf(student_id)
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_card_{student_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/fee-receipt/{payment_id}/pdf")
async def export_fee_receipt_pdf(
    payment_id: str,
    school_id: str
):
    """
    Generate PDF fee receipt
    
    Path params:
    - payment_id: Payment ID
    
    Query params:
    - school_id: School ID
    """
    try:
        export_service = get_export_service(school_id)
        pdf_data = export_service.export_fee_receipt_pdf(payment_id)
        
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=receipt_{payment_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXPORT FORMATS INFO
# ============================================================================

@router.get("/export/formats")
async def get_export_formats():
    """Get information about available export formats"""
    return {
        "csv_exports": {
            "students": {
                "endpoint": "GET /api/export/students/csv",
                "params": ["school_id (required)", "class_name (optional)"],
                "description": "Export student list with all details"
            },
            "attendance": {
                "endpoint": "GET /api/export/attendance/csv",
                "params": ["school_id (required)", "start_date (optional)", "end_date (optional)", "class_name (optional)"],
                "description": "Export attendance records for date range"
            },
            "grades": {
                "endpoint": "GET /api/export/grades/csv",
                "params": ["school_id (required)", "assessment_name (optional)", "class_name (optional)"],
                "description": "Export grades for assessments"
            },
            "fees": {
                "endpoint": "GET /api/export/fees/csv",
                "params": ["school_id (required)", "status (optional)"],
                "description": "Export fee records and balances"
            }
        },
        "pdf_exports": {
            "report_card": {
                "endpoint": "GET /api/export/report-card/{student_id}/pdf",
                "params": ["student_id (path)", "school_id (query)"],
                "description": "Generate PDF report card for student"
            },
            "fee_receipt": {
                "endpoint": "GET /api/export/fee-receipt/{payment_id}/pdf",
                "params": ["payment_id (path)", "school_id (query)"],
                "description": "Generate PDF fee receipt"
            }
        },
        "use_cases": [
            "Export student data to Excel for analysis",
            "Generate report cards for printing",
            "Create fee receipts for parents",
            "Export attendance for ministry reporting",
            "Backup data in CSV format"
        ]
    }
