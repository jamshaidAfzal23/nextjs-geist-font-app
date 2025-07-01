"""
User model for Smart CRM SaaS application.
This module defines the User database model and related functionality.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class User(Base):
    """
    User model representing system users (developers, managers, admins).
    
    This model stores user information including authentication details,
    role-based access control, and relationships to other entities.
    
    Attributes:
        id (int): Primary key, auto-incrementing user ID
        full_name (str): User's full name
        email (str): Unique email address for authentication
        hashed_password (str): Bcrypt hashed password
        role (str): User role (admin, manager, developer, viewer)
        is_active (bool): Whether the user account is active
        is_verified (bool): Whether the user's email is verified
        created_at (datetime): Timestamp when user was created
        updated_at (datetime): Timestamp when user was last updated
        
    Relationships:
        managed_clients: Clients assigned to this user
        assigned_projects: Projects where this user is the developer
        created_expenses: Expenses created by this user
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, doc="Unique user identifier")
    
    # User information
    full_name = Column(
        String(100), 
        nullable=False, 
        doc="User's full name for display purposes"
    )
    email = Column(
        String(255), 
        unique=True, 
        index=True, 
        nullable=False,
        doc="Unique email address used for authentication"
    )
    hashed_password = Column(
        String(255), 
        nullable=False,
        doc="Bcrypt hashed password for secure authentication"
    )
    
    # Role and permissions
    role = Column(
        String(50), 
        nullable=False, 
        default="user",
        index=True,
        doc="User role determining access permissions (admin, manager, developer, viewer)"
    )
    
    # Account status
    is_active = Column(
        Boolean, 
        default=True,
        doc="Whether the user account is active and can log in"
    )
    is_verified = Column(
        Boolean, 
        default=False,
        doc="Whether the user's email address has been verified"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        doc="Timestamp when the user account was created"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        doc="Timestamp when the user account was last updated"
    )
    
    # Relationships
    managed_clients = relationship(
        "Client", 
        back_populates="assigned_user",
        doc="Clients assigned to this user for management"
    )
    assigned_projects = relationship(
        "Project", 
        back_populates="developer",
        doc="Projects where this user is assigned as the developer"
    )
    created_expenses = relationship(
        "Expense", 
        back_populates="created_by_user",
        doc="Expenses created by this user"
    )
    api_keys = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    preferences = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of the User object."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation of the User object."""
        return f"{self.full_name} ({self.email})"
