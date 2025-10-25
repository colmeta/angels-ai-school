"""
Health Check Endpoints - WITH DEBUGGING
"""
from fastapi import APIRouter
import os
import sys
from pathlib import Path

# Debug: Print current file location
current_file = Path(__file__)
print(f"🔍 Current file: {current_file}")
print(f"🔍 Current file absolute: {current_file.resolve()}")

# Try different parent levels
for i in range(1, 5):
    parent = current_file
    for _ in range(i):
        parent = parent.parent
    print(f"🔍 Parent level {i}: {parent.resolve()}")
    print(f"   - Exists: {parent.exists()}")
    if parent.exists():
        print(f"   - Contents: {list(parent.iterdir())[:5]}")  # First 5 items

# Add project root to path - try parent.parent.parent
project_root = Path(__file__).parent.parent.parent
print(f"🔍 Adding to sys.path: {project_root.resolve()}")

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"🔍 sys.path: {sys.path[:3]}")

# Try to import
try:
    from database import get_db
    print("✅ Successfully imported database!")
except ImportError as e:
    print(f"❌ Failed to import database: {e}")
    # Try to find database.py
    for path in sys.path[:5]:
        db_file = Path(path) / "database.py"
        print(f"🔍 Checking: {db_file}")
        print(f"   - Exists: {db_file.exists()}")

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
        from database import get_db
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