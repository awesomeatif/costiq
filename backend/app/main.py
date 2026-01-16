"""
CostIQ Backend - Main Application Entry Point

This is the main FastAPI application that:
1. Initializes the database
2. Sets up CORS middleware
3. Mounts all API routes
4. Provides health check endpoints

Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    On startup:
    - Initialize database tables
    - Create default data if needed
    
    On shutdown:
    - Clean up resources if needed
    """
    # Startup: Initialize database
    print("Starting CostIQ Backend...")
    init_db()
    print("Database initialized successfully!")
    
    yield  # Application runs here
    
    # Shutdown: Cleanup
    print("Shutting down CostIQ Backend...")


# Create the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## CostIQ API
    
    A B2B SaaS platform helping mid-size hospitals identify actionable operational savings.
    
    ### Features
    - **File Upload**: Upload CSV files for procurement, inventory, and labor data
    - **Data Normalization**: Automatic standardization of column names and formats
    - **Cost Analysis**: Rule-based detection of cost leakages (coming soon)
    - **Reporting**: Generate PDF reports with findings (coming soon)
    
    ### File Types Supported
    - `po`: Purchase Order data
    - `invoice`: Invoice data
    - `inventory`: Inventory snapshot data
    - `equipment`: Equipment usage data
    - `labor`: Labor/staffing data
    """,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend access
# In production, you'd want to restrict this to specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://yourfrontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint - basic info about the API.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        - status: "healthy" if all systems operational
        - database: database connection status
        - version: current application version
    """
    # In a production setup, you'd also check:
    # - Database connectivity
    # - External service availability
    # - Disk space, memory, etc.
    
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production"
    }


@app.get("/health/ready", tags=["Health"])
def readiness_check():
    """
    Readiness check - indicates if the service is ready to accept traffic.
    
    This is used by Kubernetes/containers to know when to start
    routing traffic to this instance.
    """
    return {
        "ready": True,
        "message": "Service is ready to accept requests"
    }


@app.get("/health/live", tags=["Health"])
def liveness_check():
    """
    Liveness check - indicates if the service is alive.
    
    This is used by Kubernetes/containers to know if the service
    needs to be restarted.
    """
    return {
        "alive": True,
        "message": "Service is alive"
    }


# ============================================================================
# Mount API Routers
# ============================================================================

# Mount the v1 API router
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run the application with uvicorn
    # In production, you'd use gunicorn with uvicorn workers
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
