"""
Client model for Smart CRM SaaS application.
This module defines the Client database model and related functionality.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Client(Base):
    """
    Client model representing business clients in the CRM system.
    
    This model stores client information, contact details, and manages
    relationships with projects, invoices, and assigned users.
    
    Attributes:
        id (int): Primary key, auto-incrementing client ID
        company_name (str): Official company/business name
        contact_person_name (str): Primary contact person's name
        email (str): Primary email address for communication
        phone_number (str): Primary phone number
        address (Text): Complete business address
        industry (str): Industry/business sector
        platform_preference (str): Preferred platform for projects
        notes (Text): Additional notes about the client
        assigned_user_id (int): Foreign key to the user managing this client
        created_at (datetime): Timestamp when client was added
        updated_at (datetime): Timestamp when client was last updated
        
    Relationships:
        assigned_user: User responsible for managing this client
        projects: All projects associated with this client
        invoices: All invoices sent to this client
        payments: All payments received from this client
    """
    
    __tablename__ = "clients"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, doc="Unique client identifier")
    
    # Company information
    company_name = Column(
        String(200), 
        nullable=False, 
        index=True,
        doc="Official company or business name"
    )
    contact_person_name = Column(
        String(100), 
        nullable=False,
        doc="Name of the primary contact person"
    )
    
    # Contact information
    email = Column(
        String(255), 
        nullable=False, 
        index=True,
        doc="Primary email address for client communication"
    )
    phone_number = Column(
        String(20),
        doc="Primary phone number for client contact"
    )
    address = Column(
        Text,
        doc="Complete business address including street, city, state, zip"
    )
    
    # Business details
    industry = Column(
        String(100),
        doc="Industry or business sector (e.g., Healthcare, Finance, E-commerce)"
    )
    platform_preference = Column(
        String(100),
        doc="Preferred platform for projects (e.g., Web, Mobile, Desktop)"
    )
    
    # Additional information
    notes = Column(
        Text,
        doc="Additional notes, preferences, or important information about the client"
    )
    
    # Foreign keys
    assigned_user_id = Column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=False,
        doc="ID of the user responsible for managing this client"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        doc="Timestamp when the client was added to the system"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        doc="Timestamp when the client information was last updated"
    )
    
    # Relationships
    assigned_user = relationship(
        "User", 
        back_populates="managed_clients",
        doc="User responsible for managing this client relationship"
    )
    projects = relationship(
        "Project", 
        back_populates="client",
        cascade="all, delete-orphan",
        doc="All projects associated with this client"
    )
    invoices = relationship(
        "Invoice", 
        back_populates="client",
        cascade="all, delete-orphan",
        doc="All invoices sent to this client"
    )
    payments = relationship(
        "Payment", 
        back_populates="client",
        doc="All payments received from this client"
    )
    
    def __repr__(self) -> str:
        """String representation of the Client object."""
        return f"<Client(id={self.id}, company='{self.company_name}', contact='{self.contact_person_name}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation of the Client object."""
        return f"{self.company_name} - {self.contact_person_name}"
    
    @property
    def total_project_value(self) -> float:
        """
        Calculate the total value of all projects for this client.
        
        Returns:
            float: Sum of all project values for this client
        """
        return sum(project.total_amount for project in self.projects if project.total_amount)
    
    @property
    def active_projects_count(self) -> int:
        """
        Count the number of active projects for this client.
        
        Returns:
            int: Number of projects with status 'active' or 'in_progress'
        """
        active_statuses = ['active', 'in_progress', 'development']
        return len([p for p in self.projects if p.status in active_statuses])
