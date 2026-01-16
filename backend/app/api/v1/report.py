"""
Report API Endpoints

PDF report generation endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.finding import Finding
from app.services.pdf_generator import generate_report


router = APIRouter()


@router.get("/pdf")
def download_pdf_report(
    org_name: str = "Your Hospital",
    db: Session = Depends(get_db)
):
    """
    Generate and download the Cost Optimization Diagnostic PDF.
    
    Query params:
    - org_name: Organization name to display on the report
    
    Returns: PDF file download
    """
    # Get all findings from database
    findings = db.query(Finding).order_by(Finding.created_at.desc()).all()
    
    if not findings:
        raise HTTPException(
            status_code=404,
            detail="No findings available. Run analysis first using POST /api/v1/analyze/run"
        )
    
    # Generate PDF
    pdf_buffer = generate_report(findings, org_name)
    
    # Return as downloadable file
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=CostIQ_Diagnostic_Report.pdf"
        }
    )
