"""
Labor Data Model

Stores normalized labor and staffing data.
Used to detect overtime anomalies relative to patient volume.
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class LaborData(Base, TimestampMixin):
    """
    Labor data model for storing staffing and overtime information.
    
    This table stores normalized labor data from HR/scheduling systems.
    Combined with patient census data to identify overtime anomalies.
    
    Rules that use this data:
    - Overtime vs Patient Volume Mismatch: Flag high overtime on low-volume days
    """
    __tablename__ = "labor_data"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to upload batch
    batch_id = Column(
        Integer,
        ForeignKey("upload_batches.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Department/unit information
    department = Column(String(100), nullable=False, index=True)
    cost_center = Column(String(100), nullable=True)
    
    # Staff identification (anonymized)
    staff_id = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    staff_type = Column(String(50), nullable=True)  # RN, CNA, Tech, etc.
    
    # Shift information
    shift_date = Column(Date, nullable=False, index=True)
    shift_type = Column(String(50), nullable=True)  # Day, Night, Swing
    
    # Hours worked
    scheduled_hours = Column(Float, nullable=True)
    hours_worked = Column(Float, nullable=False)
    overtime_hours = Column(Float, nullable=True, default=0.0)
    
    # Pay information (for calculating costs)
    regular_rate = Column(Float, nullable=True)
    overtime_rate = Column(Float, nullable=True)
    total_labor_cost = Column(Float, nullable=True)
    
    # Patient volume (for correlation analysis)
    # This might come from the same file or be joined from another source
    patient_volume_metric = Column(Float, nullable=True)  # Census, admissions, etc.
    
    # Relationship back to batch
    batch = relationship("UploadBatch", back_populates="labor_data")
    
    def __repr__(self):
        return f"<LaborData(id={self.id}, dept='{self.department}', date={self.shift_date})>"
