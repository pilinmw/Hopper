"""
FastAPI Main Application

RESTful API for document merging service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routes import upload_router, merge_router, download_router
from api.models.task import HealthResponse

# Create FastAPI app
app = FastAPI(
    title="Smart Document Factory API",
    description="RESTful API for merging multiple document formats into Excel",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track app start time
start_time = datetime.now()

# Include routers
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(merge_router, prefix="/api/v1", tags=["Merge"])
app.include_router(download_router, prefix="/api/v1", tags=["Download"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Document Factory API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    uptime = datetime.now() - start_time
    uptime_seconds = int(uptime.total_seconds())
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime=f"{uptime_seconds}s"
    )


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 Starting Smart Document Factory API")
    print("=" * 60)
    print("📖 API Docs: http://localhost:8000/api/docs")
    print("💊 Health Check: http://localhost:8000/api/health")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
