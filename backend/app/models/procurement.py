"""
Procurement Data Model

Stores normalized procurement data (POs and Invoices).
Simplified for MVP - core fields only.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from datetime import datetime

from app.core.database import Base


class ProcurementData(Base):
    """
    Procurement data model for purchase orders and invoices.
    
    Used by rules:
    - Vendor Price Variance
    - Contract vs Invoice Mismatch
    """
    __tablename__ = "procurement_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Vendor info
    vendor_name = Column(String(255), nullable=False, index=True)
    
    # Item info
    item_sku = Column(String(100), nullable=False, index=True)
    item_description = Column(String(500), nullable=True)
    
    # Pricing
    unit_price = Column(Float, nullable=False)
    quantity = Column(Float, default=1.0)
    
    # Contract reference (for mismatch detection)
    contract_price = Column(Float, nullable=True)
    
    # Order info
    po_number = Column(String(100), nullable=True)
    po_date = Column(Date, nullable=True)
    department = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProcurementData(sku='{self.item_sku}', price={self.unit_price})>"
