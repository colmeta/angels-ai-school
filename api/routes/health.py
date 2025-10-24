"""
Health Check Endpoints
"""
from fastapi import APIRouter, Depends
from database import get_db
import os

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
