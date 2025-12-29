"""
Universal Import API Endpoint
Handles file uploads and import preview/execution
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import tempfile
import os

from ..services.universal_import import UniversalImporter

router = APIRouter(prefix="/api/import", tags=["import"])

@router.post("/preview")
async def preview_import(
    file: UploadFile = File(...),
    school_id: str = "demo-school"  # TODO: Get from auth
):
    """
    Upload a file and preview the import mapping
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Supported: .xlsx, .xls, .csv"
        )
    
    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        importer = UniversalImporter(school_id)
        preview = importer.preview_import(tmp_path)
        
        return JSONResponse({
            "status": "success",
            "data": preview,
            "message": f"Detected {len(preview['detected_mapping'])} fields. Confidence: {preview['confidence']*100}%"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/execute")
async def execute_import(
    file: UploadFile = File(...),
    school_id: str = "demo-school",  # TODO: Get from auth
    confirm: bool = True
):
    """
    Execute the import after user confirms the preview
    """
    if not confirm:
        raise HTTPException(status_code=400, detail="Import not confirmed")
    
    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        importer = UniversalImporter(school_id)
        result = importer.execute_import(tmp_path)
        
        # TODO: Actually insert into database here
        # For now, returning the data
        
        return JSONResponse({
            "status": "success",
            "data": {
                "imported_count": result['imported_count'],
                "students": result['students'][:10]  # First 10 for confirmation
            },
            "message": f"Successfully imported {result['imported_count']} students!"
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
