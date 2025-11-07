from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from api.core.config import get_settings
from api.routes import agents, clarity, fees, health, parents, schools, students

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

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(fees.router, prefix="/api/fees", tags=["Fees"])
app.include_router(parents.router, prefix="/api/parents", tags=["Parents"])
app.include_router(agents.router, prefix="/api/agents", tags=["AI Agents"])
app.include_router(clarity.router, prefix="/api/clarity", tags=["Clarity Engine"])
app.include_router(schools.router, prefix="/api/schools", tags=["School Configuration"])

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