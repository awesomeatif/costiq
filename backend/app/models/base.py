"""
Base Model Configuration

This module provides common base classes and mixins for all models.
Includes timestamp mixins and common column patterns.
"""

from sqlalchemy import Column, DateTime, func
from app.core.database import Base


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps to models.
    
    These fields are automatically managed:
    - created_at: Set when record is first created
    - updated_at: Updated whenever record is modified
    """
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
