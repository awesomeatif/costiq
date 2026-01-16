"""
API v1 Router

Aggregates all v1 API routes.
"""

from fastapi import APIRouter

from app.api.v1 import uploads, analyze, report

api_router = APIRouter()

# File upload endpoints
api_router.include_router(
    uploads.router,
    prefix="/uploads",
    tags=["File Uploads"]
)

# Analysis endpoints (rules engine)
api_router.include_router(
    analyze.router,
    prefix="/analyze",
    tags=["Analysis"]
)

# Report endpoints (PDF generation)
api_router.include_router(
    report.router,
    prefix="/report",
    tags=["Reports"]
)
