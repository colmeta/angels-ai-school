"""
Data Migration Routes
Import data from ANY old system → Auto-organize
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from api.services.data_migration import DataMigrationService

router = APIRouter(tags=["Data Migration"])


@router.post("/migrate/import-file")
async def import_data_file(
    school_id: str = Form(...),
    file: UploadFile = File(...),
    data_type: Optional[str] = Form(None)
):
    """
    Import data from ANY old system
    
    Supported formats:
    - CSV (Excel export)
    - JSON
    - TSV
    - Plain text (comma/tab separated)
    
    Supported data types (auto-detected):
    - Students
    - Teachers
    - Parents
    - Payments/Fees
    - Grades/Results
    - Attendance
    - Expenses
    
    AI will:
    1. Detect what type of data you have
    2. Map fields to our database
    3. Import everything automatically
    4. Handle duplicates intelligently
    """
    try:
        content = await file.read()
        
        migration_service = DataMigrationService(school_id)
        result = await migration_service.import_data(
            file_content=content,
            filename=file.filename,
            data_type=data_type
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/migrate/batch-import")
async def batch_import_files(
    school_id: str = Form(...),
    files: list[UploadFile] = File(...)
):
    """
    Import multiple files at once
    
    Example:
    - students.csv → Auto-imports all students
    - payments.xlsx → Auto-imports all payments
    - grades.json → Auto-imports all grades
    
    All in one go!
    """
    try:
        results = []
        migration_service = DataMigrationService(school_id)
        
        for file in files:
            content = await file.read()
            result = await migration_service.import_data(
                file_content=content,
                filename=file.filename,
                data_type=None
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


@router.get("/migrate/examples")
async def get_migration_examples():
    """Get examples of data formats that can be imported"""
    return {
        "students_csv": {
            "format": "CSV",
            "required_fields": ["first_name", "last_name"],
            "optional_fields": ["admission_number", "class", "gender", "date_of_birth"],
            "example": """first_name,last_name,class,admission_number
John,Doe,Class 5A,2024001
Mary,Smith,Primary 3,2024002"""
        },
        "payments_csv": {
            "format": "CSV",
            "required_fields": ["student", "amount"],
            "optional_fields": ["date", "method", "receipt_number"],
            "example": """student,amount,date,method
John Doe,50000,2025-11-01,cash
2024002,75000,2025-11-02,mobile_money"""
        },
        "teachers_csv": {
            "format": "CSV",
            "required_fields": ["first_name", "last_name"],
            "optional_fields": ["email", "phone", "subjects"],
            "example": """first_name,last_name,email,subjects
Jane,Teacher,jane@school.com,Math Science
Peter,Instructor,peter@school.com,English"""
        },
        "expenses_csv": {
            "format": "CSV",
            "required_fields": ["category", "amount"],
            "optional_fields": ["date", "description", "vendor"],
            "example": """category,amount,date,description
Utilities,120000,2025-11-01,Electricity bill
Supplies,45000,2025-11-02,Stationery"""
        },
        "flexible_format": {
            "note": "AI can understand almost any format!",
            "examples": [
                "Different column names (First Name vs first_name vs fname)",
                "Extra columns (will be ignored)",
                "Different orders (columns don't need to be in specific order)",
                "Missing optional fields (will use defaults)"
            ]
        }
    }
