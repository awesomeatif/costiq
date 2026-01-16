"""
User Model

Represents users who can access the CostIQ system.
Users belong to an organization and have roles.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base
from app.models.base import TimestampMixin


class UserRole(str, enum.Enum):
    """
    User roles determine access levels within the system.
    
    - ADMIN: Full access, can manage users and settings
    - ANALYST: Can upload data, run analysis, view reports
    - VIEWER: Read-only access to dashboards and reports
    """
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base, TimestampMixin):
    """
    User model for authentication and authorization.
    
    Each user belongs to exactly one organization and has a role
    that determines their permissions within the system.
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Email is used for login - must be unique
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Password is stored as a hash (never plain text!)
    # Using bcrypt via passlib
    hashed_password = Column(String(255), nullable=False)
    
    # User's display name
    full_name = Column(String(255), nullable=True)
    
    # Role determines permissions
    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.ANALYST
    )
    
    # Foreign key to organization
    org_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Relationship back to organization
    organization = relationship("Organization", back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role={self.role})>"
