from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv()

from api.core.config import get_settings
from api.middleware.rate_limiter import rate_limit_middleware
from api.middleware.audit import AuditMiddleware
from api.core.circuit_breakers import CircuitBreakerOpenException
from api.middleware.memory_monitor import MemoryMonitorMiddleware

settings = get_settings()

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("angels.api")

# Initialize MCP Provider
from api.services.clarity import get_clarity_client
get_clarity_client()

# Create FastAPI app
app = FastAPI(
    title=f"{settings.default_brand_name} API",
    description="Complete Educational Revolution Platform for African Schools",
    version="1.0.0",
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None,
    contact={
        "name": settings.default_brand_name,
        "url": "https://your-school-domain.com",
    },
)

# Global Exception Handler for Circuit Breakers
@app.exception_handler(CircuitBreakerOpenException)
async def circuit_breaker_handler(request: Request, exc: CircuitBreakerOpenException):
    return JSONResponse(
        status_code=503,
        content={"error": "Service temporarily degraded. Operating in Safe Mode.", "retry_after": 60}
    )

# Security & Performance Middlewares
# Allow all hosts in production (Render, custom domains)
# Security is maintained through CORS middleware below
allowed_hosts = ["*"] if settings.environment == "production" else ["localhost", "127.0.0.1"]
if settings.allowed_brand_domains and settings.environment != "production":
    allowed_hosts.extend(settings.allowed_brand_domains)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
app.add_middleware(GZipMiddleware, minimum_size=1000)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    settings.frontend_url,
]
if settings.allowed_brand_domains:
    origins.extend([f"https://{d}" for d in settings.allowed_brand_domains])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if settings.environment == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuditMiddleware)
app.add_middleware(MemoryMonitorMiddleware, max_memory_mb=400)
app.middleware("http")(rate_limit_middleware)

# Import and include all routes
from api.routes import (
    agents, auth, auth_google, students, fees, parents, teachers, 
    parent_portal, student_portal, director, inventory, ai, documents, 
    attendance, health, bulk_operations, command_intelligence, 
    document_intelligence, data_migration, domain_intelligence, export, 
    multi_role, multi_school, requirements, schools, payments, chatbot, 
    support, analytics, discounts, transport, boarding, 
    government_reporting, feeding, library, discipline, homework, events, 
    messaging, ussd, whatsapp, translation, uneb, monitoring, canteen, 
    payroll, alumni, clarity, finance, experiments, reports
)

from api.routers import (
    ussd_webhook, whatsapp_webhook, universal_import, 
    school_registration, receptionist, branding
)

# Core Platform Routes
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(auth_google.router, prefix="/api", tags=["Google Authentication"])
app.include_router(bulk_operations.router, prefix="/api", tags=["Bulk Operations"])
app.include_router(command_intelligence.router, prefix="/api", tags=["Command Intelligence"])
app.include_router(document_intelligence.router, prefix="/api", tags=["Document Intelligence"])
app.include_router(data_migration.router, prefix="/api", tags=["Data Migration"])
app.include_router(domain_intelligence.router, prefix="/api", tags=["Domain Intelligence"])
app.include_router(export.router, prefix="/api", tags=["Data Export"])
app.include_router(multi_role.router, prefix="/api", tags=["Multi-Role"])
app.include_router(multi_school.router, prefix="/api", tags=["Multi-School"])
app.include_router(requirements.router, prefix="/api", tags=["School Requirements"])

app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(fees.router, prefix="/api/fees", tags=["Fees"])
app.include_router(parents.router, prefix="/api/parents", tags=["Parents"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["AI Agents"])
app.include_router(director.router, prefix="/api/v1", tags=["Director"])
app.include_router(inventory.router, prefix="/api/v1", tags=["Inventory"])
app.include_router(clarity.router, prefix="/api/v1/clarity", tags=["Clarity Engine"])
app.include_router(ai.router, tags=["AI System"])
app.include_router(documents.router, tags=["Documents & Photos"])
app.include_router(finance.router, prefix="/api/v1", tags=["Financial Intelligence"])
app.include_router(experiments.router, tags=["A/B Testing & Experiments"])

app.include_router(schools.router, prefix="/api/schools", tags=["School Configuration"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])
app.include_router(support.router, prefix="/api", tags=["Support Operations"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teacher Workflows"])
app.include_router(parent_portal.router, prefix="/api/parent", tags=["Parent Portal"])
app.include_router(student_portal.router, prefix="/api/student", tags=["Student Portal"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics & Dashboards"])

app.include_router(discounts.router, prefix="/api", tags=["Sibling Discounts & Payment Plans"])
app.include_router(transport.router, prefix="/api", tags=["School Transport"])
app.include_router(boarding.router, prefix="/api", tags=["Boarding School"])
app.include_router(government_reporting.router, prefix="/api", tags=["Government Reporting"])
app.include_router(feeding.router, prefix="/api", tags=["School Feeding"])
app.include_router(library.router, prefix="/api", tags=["Library Management"])
app.include_router(discipline.router, prefix="/api", tags=["Disciplinary Records"])
app.include_router(homework.router, prefix="/api", tags=["Homework Tracking"])
app.include_router(events.router, prefix="/api", tags=["School Events"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

app.include_router(messaging.router, prefix="/api", tags=["Internal Messaging (Free)"])
app.include_router(ussd.router, prefix="/api", tags=["USSD Support"])
app.include_router(whatsapp.router, prefix="/api", tags=["WhatsApp Integration"])
app.include_router(translation.router, prefix="/api", tags=["Multi-Language Support"])
app.include_router(uneb.router, prefix="/api", tags=["UNEB Integration"])

app.include_router(ussd_webhook.router, tags=["USSD Webhooks"])
app.include_router(whatsapp_webhook.router, tags=["WhatsApp Webhooks"])
app.include_router(universal_import.router, tags=["Universal Import"])
app.include_router(school_registration.router, tags=["School Registration"])
app.include_router(receptionist.router, tags=["24/7 AI Receptionist"])
app.include_router(branding.router, tags=["Dynamic Branding"])
app.include_router(attendance.router, tags=["Attendance (Dynamic)"])

app.include_router(canteen.router, prefix="/api", tags=["Canteen/Tuck Shop"])
app.include_router(payroll.router, prefix="/api", tags=["Staff Payroll"])
app.include_router(alumni.router, prefix="/api", tags=["Alumni Tracking"])
app.include_router(monitoring.router, prefix="/api", tags=["Monitoring"])

@app.get("/")
async def root():
    return {
        "message": f"{settings.default_brand_name} API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "branding": {
            "primary_color": settings.default_brand_primary_color,
            "accent_color": settings.default_brand_accent_color,
            "logo_url": settings.default_brand_logo_url,
        },
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
