from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from api.core.config import get_settings
from api.routes import (
    agents,
    alumni,
    analytics,
    auth,
    boarding,
    bulk_operations,
    canteen,
    clarity,
    command_intelligence,
    data_migration,
    discipline,
    discounts,
    document_intelligence,
    domain_intelligence,
    events,
    export,
    feeding,
    fees,
    government_reporting,
    health,
    homework,
    library,
    monitoring,
    multi_role,
    multi_school,
    parents,
    payroll,
    payments,
    requirements,
    schools,
    students,
    chatbot,
    support,
    teachers,
    transport,
    parent_portal,
    student_portal,
    translation,
    uneb,
    ussd,
    whatsapp,
)
from api.middleware.rate_limiter import rate_limit_middleware

# Add project root to path FIRST
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv()
settings = get_settings()

# Create FastAPI app with branding-aware metadata
app = FastAPI(
    title=f"{settings.default_brand_name} API",
    description="Complete Educational Revolution Platform for African Schools",
    version="1.0.0",
    contact={
        "name": settings.default_brand_name,
        "url": "https://your-school-domain.com",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(bulk_operations.router, prefix="/api", tags=["Bulk Operations"])
app.include_router(command_intelligence.router, prefix="/api", tags=["Command Intelligence"])
app.include_router(document_intelligence.router, prefix="/api", tags=["Document Intelligence"])
app.include_router(data_migration.router, prefix="/api", tags=["Data Migration"])
app.include_router(domain_intelligence.router, prefix="/api", tags=["Domain Intelligence"])
app.include_router(export.router, prefix="/api", tags=["Data Export"])
app.include_router(multi_role.router, prefix="/api", tags=["Multi-Role"])
app.include_router(multi_school.router, prefix="/api", tags=["Multi-School"])
app.include_router(requirements.router, prefix="/api", tags=["School Requirements"])

# Core Platform Routes
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(fees.router, prefix="/api/fees", tags=["Fees"])
app.include_router(parents.router, prefix="/api/parents", tags=["Parents"])
app.include_router(agents.router, prefix="/api/agents", tags=["AI Agents"])
app.include_router(clarity.router, prefix="/api/clarity", tags=["Clarity Engine"])
app.include_router(schools.router, prefix="/api/schools", tags=["School Configuration"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(chatbot.router, prefix="/api", tags=["Chatbot"])
app.include_router(support.router, prefix="/api", tags=["Support Operations"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teacher Workflows"])
app.include_router(parent_portal.router, prefix="/api/parent", tags=["Parent Portal"])
app.include_router(student_portal.router, prefix="/api/student", tags=["Student Portal"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics & Dashboards"])

# 10 Critical Features (Option 2)
app.include_router(discounts.router, prefix="/api", tags=["Sibling Discounts & Payment Plans"])
app.include_router(transport.router, prefix="/api", tags=["School Transport"])
app.include_router(boarding.router, prefix="/api", tags=["Boarding School"])
app.include_router(government_reporting.router, prefix="/api", tags=["Government Reporting"])
app.include_router(feeding.router, prefix="/api", tags=["School Feeding"])
app.include_router(library.router, prefix="/api", tags=["Library Management"])
app.include_router(discipline.router, prefix="/api", tags=["Disciplinary Records"])
app.include_router(homework.router, prefix="/api", tags=["Homework Tracking"])
app.include_router(events.router, prefix="/api", tags=["School Events"])

# Communication & Integration (Top 6 from Field Research)
app.include_router(ussd.router, prefix="/api", tags=["USSD Support"])
app.include_router(whatsapp.router, prefix="/api", tags=["WhatsApp Integration"])
app.include_router(translation.router, prefix="/api", tags=["Multi-Language Support"])
app.include_router(uneb.router, prefix="/api", tags=["UNEB Integration"])

# Additional Critical Features (Phase 3)
app.include_router(canteen.router, prefix="/api", tags=["Canteen/Tuck Shop"])
app.include_router(payroll.router, prefix="/api", tags=["Staff Payroll"])
app.include_router(alumni.router, prefix="/api", tags=["Alumni Tracking"])

# Production Monitoring
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