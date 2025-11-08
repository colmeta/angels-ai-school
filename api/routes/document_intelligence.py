"""
Document Intelligence Routes
Upload ANY document → Auto-extract → Auto-organize
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from api.services.document_intelligence import DocumentIntelligenceService

router = APIRouter(tags=["Document Intelligence"])


@router.post("/documents/upload")
async def upload_document(
    school_id: str = Form(...),
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None)
):
    """
    Upload ANY document and let AI extract and organize data
    
    Supported documents:
    - Student records → Auto-creates students
    - Fee receipts → Auto-records payments
    - Report cards → Auto-records grades
    - Attendance sheets → Auto-marks attendance
    - Contracts → Auto-analyzes and stores
    - Budget sheets → Auto-records expenses
    - Health records → Auto-records health visits
    - Inventory lists → Auto-updates inventory
    
    Just upload the photo/PDF and watch the magic!
    """
    try:
        content = await file.read()
        
        doc_service = DocumentIntelligenceService(school_id)
        result = await doc_service.process_document(
            file_content=content,
            filename=file.filename,
            document_type=document_type
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/batch-upload")
async def batch_upload_documents(
    school_id: str = Form(...),
    files: list[UploadFile] = File(...)
):
    """
    Upload multiple documents at once
    Perfect for migrating old hard-copy records
    
    Example: Upload 100 old student record cards → All auto-processed
    """
    try:
        results = []
        doc_service = DocumentIntelligenceService(school_id)
        
        for file in files:
            content = await file.read()
            result = await doc_service.process_document(
                file_content=content,
                filename=file.filename,
                document_type=None  # Auto-detect
            )
            results.append({
                "filename": file.filename,
                "result": result
            })
        
        return {
            "success": True,
            "total_files": len(files),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/examples")
async def get_document_examples():
    """Get examples of what documents can be processed"""
    return {
        "student_records": {
            "description": "Old student registration forms, admission cards",
            "extracts": ["Name", "DOB", "Class", "Admission Number", "Parent Info"],
            "action": "Creates student record in database"
        },
        "payment_receipts": {
            "description": "Fee receipts, payment slips",
            "extracts": ["Student Name", "Amount", "Date", "Payment Method"],
            "action": "Records payment in database, updates fee status"
        },
        "report_cards": {
            "description": "Exam results, progress reports",
            "extracts": ["Student Name", "Subjects", "Marks", "Grades"],
            "action": "Records all grades in database, notifies parents"
        },
        "attendance_sheets": {
            "description": "Daily attendance registers",
            "extracts": ["Date", "Student Names", "Present/Absent Status"],
            "action": "Marks attendance for all students, notifies parents"
        },
        "contracts": {
            "description": "Employment contracts, service agreements",
            "extracts": ["Parties", "Terms", "Dates", "Payment Terms", "Liabilities"],
            "action": "Legal analysis, stores contract details"
        },
        "budget_sheets": {
            "description": "Expense reports, budget allocations",
            "extracts": ["Categories", "Amounts", "Dates", "Vendors"],
            "action": "Records all expenses, generates insights"
        },
        "health_records": {
            "description": "Sickbay registers, medical forms",
            "extracts": ["Student Name", "Symptoms", "Treatment", "Date"],
            "action": "Records health visit, notifies parents if serious"
        },
        "inventory_lists": {
            "description": "Stock lists, equipment registers",
            "extracts": ["Item Names", "Quantities", "Locations", "Conditions"],
            "action": "Updates inventory database"
        },
        "any_other_document": {
            "description": "Literally any school document with text",
            "extracts": "AI auto-detects what data is important",
            "action": "Auto-organizes into appropriate database tables"
        }
    }
