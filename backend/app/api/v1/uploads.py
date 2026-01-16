"""
File Upload API Endpoints

Handles CSV file uploads and stores normalized data in database.
"""

from io import StringIO
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.models.upload import UploadBatch, FileType, UploadStatus
from app.models.procurement import ProcurementData
from app.models.inventory import InventoryData
from app.services import normalization


router = APIRouter()


# --------------------------------------------------------------------------
# Response Models
# --------------------------------------------------------------------------

class UploadResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    record_count: int
    warnings: List[str]
    message: str


class UploadHistoryItem(BaseModel):
    id: int
    filename: str
    file_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class UploadHistoryResponse(BaseModel):
    uploads: List[UploadHistoryItem]
    total: int


# --------------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------------

def store_procurement_data(records: List[dict], db: Session) -> int:
    """Store normalized procurement records in database."""
    count = 0
    for row in records:
        data = ProcurementData(
            vendor_name=row.get("vendor_name", "Unknown"),
            item_sku=row.get("item_sku", row.get("sku", "Unknown")),
            item_description=row.get("item_description", row.get("description", "")),
            unit_price=float(row.get("unit_price", 0) or 0),
            quantity=float(row.get("quantity", 1) or 1),
            contract_price=float(row.get("contract_price", 0) or 0) if row.get("contract_price") else None,
            po_number=row.get("po_number"),
            department=row.get("department")
        )
        db.add(data)
        count += 1
    return count


def store_inventory_data(records: List[dict], db: Session) -> int:
    """Store normalized inventory records in database."""
    count = 0
    for row in records:
        # Parse expiry date
        expiry = row.get("expiry_date")
        if expiry and pd.notna(expiry):
            if isinstance(expiry, str):
                try:
                    expiry = pd.to_datetime(expiry).date()
                except:
                    expiry = None
            elif hasattr(expiry, 'date'):
                expiry = expiry.date()
        else:
            expiry = None
        
        data = InventoryData(
            sku=row.get("sku", row.get("item_sku", "Unknown")),
            item_description=row.get("item_description", row.get("description", "")),
            location=row.get("location", ""),
            department=row.get("department", ""),
            quantity_on_hand=float(row.get("quantity_on_hand", 0) or 0),
            unit_cost=float(row.get("unit_cost", 0) or 0) if row.get("unit_cost") else None,
            expiry_date=expiry,
            daily_usage_rate=float(row.get("daily_usage_rate", 0) or 0) if row.get("daily_usage_rate") else None
        )
        db.add(data)
        count += 1
    return count


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV file for processing.
    
    File types: po, invoice, inventory, equipment, labor
    """
    # Validate file type
    try:
        validated_type = FileType(file_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file_type. Must be one of: {[t.value for t in FileType]}"
        )
    
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Create upload batch record
    batch = UploadBatch(
        filename=file.filename,
        file_type=validated_type,
        status=UploadStatus.PROCESSING
    )
    db.add(batch)
    db.flush()
    
    try:
        # Read and decode file
        content = await file.read()
        try:
            decoded = content.decode('utf-8')
        except UnicodeDecodeError:
            decoded = content.decode('latin-1')
        
        # Parse CSV
        df = pd.read_csv(StringIO(decoded))
        
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Normalize data (column mapping + type casting)
        records, warnings = normalization.normalize(df, file_type)
        
        # Store data based on file type
        record_count = 0
        if validated_type in [FileType.PO, FileType.INVOICE]:
            record_count = store_procurement_data(records, db)
        elif validated_type == FileType.INVENTORY:
            record_count = store_inventory_data(records, db)
        # Labor and Equipment not implemented yet
        else:
            record_count = len(records)
        
        # Update batch status
        batch.status = UploadStatus.COMPLETED
        db.commit()
        
        return UploadResponse(
            id=batch.id,
            filename=file.filename,
            file_type=validated_type.value,
            status=batch.status.value,
            record_count=record_count,
            warnings=warnings,
            message=f"Stored {record_count} records"
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        batch.status = UploadStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/history", response_model=UploadHistoryResponse)
def get_upload_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get list of previous uploads."""
    uploads = (
        db.query(UploadBatch)
        .order_by(UploadBatch.created_at.desc())
        .offset(skip)
        .limit(min(limit, 100))
        .all()
    )
    
    total = db.query(UploadBatch).count()
    
    return UploadHistoryResponse(
        uploads=[
            UploadHistoryItem(
                id=u.id,
                filename=u.filename,
                file_type=u.file_type.value,
                status=u.status.value,
                created_at=u.created_at
            )
            for u in uploads
        ],
        total=total
    )


@router.get("/{upload_id}", response_model=UploadHistoryItem)
def get_upload(upload_id: int, db: Session = Depends(get_db)):
    """Get details of a specific upload."""
    upload = db.query(UploadBatch).filter(UploadBatch.id == upload_id).first()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return UploadHistoryItem(
        id=upload.id,
        filename=upload.filename,
        file_type=upload.file_type.value,
        status=upload.status.value,
        created_at=upload.created_at
    )
