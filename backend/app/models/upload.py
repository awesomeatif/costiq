"""
Upload Batch Model

Tracks uploaded CSV files and their processing status.
Simplified for MVP - core fields only.
"""

from sqlalchemy import Column, Integer, String, Enum as SQLEnum, DateTime
import enum
from datetime import datetime

from app.core.database import Base


class FileType(str, enum.Enum):
    """Types of CSV files that can be uploaded."""
    PO = "po"
    INVOICE = "invoice"
    INVENTORY = "inventory"
    EQUIPMENT = "equipment"
    LABOR = "labor"


class UploadStatus(str, enum.Enum):
    """Status of an upload batch."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadBatch(Base):
    """
    Upload batch model - tracks each CSV file upload.
    
    Core MVP fields only:
    - id: Primary key
    - filename: Original uploaded filename
    - file_type: Type of data (po, invoice, inventory, etc.)
    - status: Processing status
    - created_at: When uploaded
    """
    __tablename__ = "upload_batches"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    status = Column(SQLEnum(UploadStatus), nullable=False, default=UploadStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UploadBatch(id={self.id}, file='{self.filename}', status={self.status})>"
