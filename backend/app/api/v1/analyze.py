"""
Analysis API Endpoints

Triggers the rules engine to analyze data and generate findings.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.finding import Finding
from app.services.rules_engine.procurement import run_all_procurement_rules
from app.services.rules_engine.inventory import run_all_inventory_rules

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


# --------------------------------------------------------------------------
# Response Models
# --------------------------------------------------------------------------

class FindingResponse(BaseModel):
    """Single finding in response."""
    id: int
    category: str
    severity: str
    description: str
    potential_savings: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    """Response from analysis run."""
    status: str
    total_findings: int
    findings_by_category: dict
    total_potential_savings: float
    findings: List[FindingResponse]


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------

@router.post("/run", response_model=AnalysisResponse)
def run_analysis(db: Session = Depends(get_db)):
    """
    Run the cost intelligence analysis.
    
    Executes all rules:
    1. Vendor Price Variance
    2. Contract vs Invoice Mismatch
    3. Overstocking
    4. Expiry Risk
    
    Generates Finding records and persists them to database.
    Returns summary with all findings.
    """
    logger.info("=" * 60)
    logger.info("ANALYSIS RUN STARTED")
    logger.info("=" * 60)
    
    all_findings = []
    
    try:
        # Run procurement rules
        logger.info("Running procurement rules...")
        procurement_findings = run_all_procurement_rules(db)
        all_findings.extend(procurement_findings)
        logger.info(f"Procurement rules generated {len(procurement_findings)} findings")
        
        # Run inventory rules
        logger.info("Running inventory rules...")
        inventory_findings = run_all_inventory_rules(db)
        all_findings.extend(inventory_findings)
        logger.info(f"Inventory rules generated {len(inventory_findings)} findings")
        
        # Persist all findings to database
        logger.info(f"Persisting {len(all_findings)} findings to database...")
        for finding in all_findings:
            db.add(finding)
        db.commit()
        
        # Refresh to get IDs
        for finding in all_findings:
            db.refresh(finding)
        
        # Calculate summary statistics
        findings_by_category = {}
        total_savings = 0.0
        
        for f in all_findings:
            # Count by category
            if f.category not in findings_by_category:
                findings_by_category[f.category] = 0
            findings_by_category[f.category] += 1
            
            # Sum potential savings
            if f.potential_savings:
                total_savings += f.potential_savings
        
        logger.info("=" * 60)
        logger.info(f"ANALYSIS COMPLETE: {len(all_findings)} findings, ${total_savings:.2f} potential savings")
        logger.info("=" * 60)
        
        return AnalysisResponse(
            status="completed",
            total_findings=len(all_findings),
            findings_by_category=findings_by_category,
            total_potential_savings=round(total_savings, 2),
            findings=[
                FindingResponse(
                    id=f.id,
                    category=f.category,
                    severity=f.severity,
                    description=f.description,
                    potential_savings=f.potential_savings,
                    created_at=f.created_at
                )
                for f in all_findings
            ]
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/findings", response_model=List[FindingResponse])
def get_findings(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all findings with optional filtering.
    
    Query params:
    - category: Filter by category (price_variance, contract_mismatch, overstock, expiry_risk)
    - severity: Filter by severity (high, medium, low)
    - skip: Pagination offset
    - limit: Max results (default 100)
    """
    query = db.query(Finding)
    
    if category:
        query = query.filter(Finding.category == category)
    if severity:
        query = query.filter(Finding.severity == severity)
    
    findings = (
        query
        .order_by(Finding.created_at.desc())
        .offset(skip)
        .limit(min(limit, 500))
        .all()
    )
    
    return [
        FindingResponse(
            id=f.id,
            category=f.category,
            severity=f.severity,
            description=f.description,
            potential_savings=f.potential_savings,
            created_at=f.created_at
        )
        for f in findings
    ]


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics of all findings.
    """
    findings = db.query(Finding).all()
    
    if not findings:
        return {
            "total_findings": 0,
            "findings_by_category": {},
            "findings_by_severity": {},
            "total_potential_savings": 0
        }
    
    by_category = {}
    by_severity = {}
    total_savings = 0.0
    
    for f in findings:
        by_category[f.category] = by_category.get(f.category, 0) + 1
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        if f.potential_savings:
            total_savings += f.potential_savings
    
    return {
        "total_findings": len(findings),
        "findings_by_category": by_category,
        "findings_by_severity": by_severity,
        "total_potential_savings": round(total_savings, 2)
    }
