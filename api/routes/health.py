"""
Health Check Endpoints
"""
from fastapi import APIRouter
import os

# Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "Angels AI API",
        "version": "1.0.0"
    }

@router.get("/health/database")
async def database_health():
    """Check database connectivity"""
    try:
        db = get_db()
        with db.get_cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@router.get("/health/env")
async def environment_check():
    """Check environment configuration"""
    required_vars = [
        "DATABASE_URL",
        "OPENAI_API_KEY"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    return {
        "status": "healthy" if not missing else "warning",
        "environment": "configured" if not missing else "incomplete",
        "missing_variables": missing if missing else None
    }