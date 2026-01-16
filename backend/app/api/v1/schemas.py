"""
Pydantic Schemas for Upload Endpoints

Defines request and response models for the upload API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums matching the database models
class FileTypeEnum(str, Enum):
    """Types of CSV files that can be uploaded."""
    PO = "po"
    INVOICE = "invoice"
    INVENTORY = "inventory"
    EQUIPMENT = "equipment"
    LABOR = "labor"


class UploadStatusEnum(str, Enum):
    """Status of an upload batch."""
    PENDING = "pending"
    VALIDATING = "validating"
    NORMALIZING = "normalizing"
    COMPLETED = "completed"
    FAILED = "failed"


# Response Models
class UploadResponse(BaseModel):
    """Response after successful file upload."""
    id: int = Field(..., description="Upload batch ID")
    filename: str = Field(..., description="Original filename")
    file_type: FileTypeEnum = Field(..., description="Type of file uploaded")
    status: UploadStatusEnum = Field(..., description="Current processing status")
    record_count: Optional[int] = Field(None, description="Number of records processed")
    warnings: List[str] = Field(default=[], description="Normalization warnings")
    message: str = Field(..., description="Status message")
    
    class Config:
        from_attributes = True


class UploadHistoryItem(BaseModel):
    """Single item in upload history."""
    id: int
    filename: str
    file_type: FileTypeEnum
    status: UploadStatusEnum
    record_count: Optional[int]
    error_message: Optional[str]
    upload_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class UploadHistoryResponse(BaseModel):
    """Response for upload history endpoint."""
    uploads: List[UploadHistoryItem]
    total_count: int


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
