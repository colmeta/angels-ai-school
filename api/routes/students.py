"""
===========================================
FILE 1: api/routes/students.py - REPLACE ENTIRE FILE
===========================================
"""
"""
Student Management Endpoints
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from pydantic import BaseModel

# FIX: Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Executive_Assistant_Service import ExecutiveAssistantService

router = APIRouter()

class StudentRegistration(BaseModel):
    school_id: str
    student: dict
    parents: list
    emergency: dict

@router.post("/register")
async def register_student(data: StudentRegistration):
    """Register a new student"""
    try:
        service = ExecutiveAssistantService(data.school_id)
        result = service.process_student_registration(data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/enrollment/{school_id}")
async def get_enrollment_stats(school_id: str, period: str = "week"):
    """Get enrollment statistics"""
    try:
        service = ExecutiveAssistantService(school_id)
        stats = service.get_enrollment_statistics(period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/{school_id}")
async def get_executive_dashboard(school_id: str, report_type: str = "daily"):
    """Get executive dashboard data"""
    try:
        service = ExecutiveAssistantService(school_id)
        report = service.generate_executive_report(report_type)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
===========================================
FILE 2: api/routes/fees.py - REPLACE ENTIRE FILE
===========================================
"""
"""
Fee Management Endpoints
"""
from fastapi import APIRouter, HTTPException

# FIX: Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Financial_Operations_Service import FinancialOperationsService

router = APIRouter()

@router.get("/ooda-loop/{school_id}")
async def run_financial_ooda_loop(school_id: str):
    """Run Financial OODA Loop"""
    try:
        service = FinancialOperationsService(school_id)
        result = service.run_ooda_loop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{school_id}")
async def get_financial_report(school_id: str):
    """Get financial report"""
    try:
        service = FinancialOperationsService(school_id)
        report = service.generate_daily_financial_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collection-summary/{school_id}")
async def get_collection_summary(school_id: str):
    """Get fee collection summary"""
    try:
        service = FinancialOperationsService(school_id)
        summary = service.fee_ops.get_fee_collection_summary(school_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
===========================================
FILE 3: api/routes/parents.py - REPLACE ENTIRE FILE
===========================================
"""
"""
Parent Engagement Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

# FIX: Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Parent_Engagement_Service import ParentEngagementService

router = APIRouter()

@router.post("/reminders/{school_id}")
async def send_fee_reminders(school_id: str, reminder_type: str = "overdue"):
    """Send fee reminders to parents"""
    try:
        service = ParentEngagementService(school_id)
        result = service.send_fee_reminders(reminder_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/event-broadcast/{school_id}")
async def broadcast_event(school_id: str, event_data: dict, target_grades: Optional[list] = None):
    """Broadcast event to parents"""
    try:
        service = ParentEngagementService(school_id)
        result = service.broadcast_event_notification(event_data, target_grades)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emergency/{school_id}/{student_id}")
async def send_emergency_notification(school_id: str, student_id: str, 
                                     emergency_type: str, details: str):
    """Send emergency notification"""
    try:
        service = ParentEngagementService(school_id)
        result = service.send_emergency_notification(student_id, emergency_type, details)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
===========================================
FILE 4: api/routes/agents.py - REPLACE ENTIRE FILE
===========================================
"""
"""
AI Agents Orchestration Endpoints
"""
from fastapi import APIRouter, HTTPException

# FIX: Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Master_Orchestrator_Complete import AngelsAIMasterOrchestrator
from Digital_CEO_Service import DigitalCEOService

router = APIRouter()

@router.get("/daily-operations/{school_id}")
async def run_daily_operations(school_id: str):
    """Run complete daily operations"""
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        result = orchestrator.run_daily_operations()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ceo-briefing/{school_id}")
async def get_ceo_briefing(school_id: str):
    """Get CEO strategic briefing"""
    try:
        service = DigitalCEOService(school_id)
        briefing = service.generate_daily_strategic_briefing()
        return briefing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fee-collection-campaign/{school_id}")
async def launch_fee_campaign(school_id: str):
    """Launch fee collection campaign"""
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        result = orchestrator.launch_fee_collection_campaign()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-report/{school_id}")
async def get_weekly_report(school_id: str):
    """Generate weekly comprehensive report"""
    try:
        orchestrator = AngelsAIMasterOrchestrator(school_id)
        report = orchestrator.generate_weekly_comprehensive_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""
===========================================
FILE 5: api/main.py - REPLACE ENTIRE FILE
===========================================
"""
"""
Angels AI - FastAPI Application
Main API entry point
"""
# FIX FOR IMPORT ERROR - ADD THESE LINES AT THE TOP
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# END FIX

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

# Import route modules
from api.routes import health, students, fees, parents, agents

# Create FastAPI app
app = FastAPI(
    title="Angels AI API",
    description="Complete Educational Revolution Platform for African Schools",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(fees.router, prefix="/api/fees", tags=["Fees"])
app.include_router(parents.router, prefix="/api/parents", tags=["Parents"])
app.include_router(agents.router, prefix="/api/agents", tags=["AI Agents"])

@app.get("/")
async def root():
    return {
        "message": "Angels AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
