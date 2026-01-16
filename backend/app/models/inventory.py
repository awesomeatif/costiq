"""
Inventory Data Model

Stores normalized inventory snapshot data.
Simplified for MVP - core fields only.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from datetime import datetime

from app.core.database import Base


class InventoryData(Base):
    """
    Inventory data model for stock level snapshots.
    
    Used by rules:
    - Overstocking
    - Expiry Risk
    """
    __tablename__ = "inventory_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Item info
    sku = Column(String(100), nullable=False, index=True)
    item_description = Column(String(500), nullable=True)
    
    # Location
    location = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Quantity and value
    quantity_on_hand = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=True)
    
    # Expiry tracking
    expiry_date = Column(Date, nullable=True)
    
    # Usage data for days-on-hand calculation
    daily_usage_rate = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<InventoryData(sku='{self.sku}', qty={self.quantity_on_hand})>"
