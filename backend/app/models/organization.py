"""
Organization (Hospital) Model

Represents a hospital/healthcare organization that uses CostIQ.
This is the top-level entity - all data belongs to an organization.
"""

from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Organization(Base, TimestampMixin):
    """
    Organization model representing a hospital or healthcare facility.
    
    Each organization has:
    - Multiple users who can access the system
    - Multiple upload batches of data
    - Configuration settings stored as JSON
    """
    __tablename__ = "organizations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Organization name (e.g., "City General Hospital")
    name = Column(String(255), nullable=False, unique=True)
    
    # Flexible settings stored as JSON
    # Can include things like:
    # - default thresholds for rules
    # - notification preferences  
    # - custom category mappings
    settings = Column(JSON, nullable=True, default={})
    
    # Relationships
    # One organization has many users
    users = relationship("User", back_populates="organization")
    
    # One organization has many upload batches
    upload_batches = relationship("UploadBatch", back_populates="organization")
    
    # One organization has many findings
    findings = relationship("Finding", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"
