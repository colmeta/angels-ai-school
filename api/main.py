"""
Angels AI - FastAPI Application
Main API entry point
"""
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
