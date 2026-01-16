"""
Finding Model

Stores cost leakage findings from analysis.
Simplified for MVP - core fields only.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
import enum
from datetime import datetime

from app.core.database import Base


class FindingSeverity(str, enum.Enum):
    """Severity levels for findings."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Finding(Base):
    """
    Finding model - stores cost leakage insights.
    
    Core MVP fields only:
    - id: Primary key
    - category: Type of finding (price_variance, overstock, etc.)
    - severity: How critical (high, medium, low)
    - description: Human-readable explanation
    - potential_savings: Estimated dollar amount
    - created_at: When identified
    """
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, default="medium")
    description = Column(String(1000), nullable=False)
    potential_savings = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Finding(id={self.id}, category='{self.category}', severity='{self.severity}')>"
