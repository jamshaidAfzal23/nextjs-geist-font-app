"""
Project model for Smart CRM SaaS application.
This module defines the Project database model and related functionality.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from datetime import datetime
from ..core.database import Base

class ProjectStatus(str, PyEnum):
    """Enumeration of possible project statuses."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Define valid project status transitions
VALID_STATUS_TRANSITIONS = {
    ProjectStatus.PLANNING: [ProjectStatus.IN_PROGRESS, ProjectStatus.ON_HOLD, ProjectStatus.CANCELLED],
    ProjectStatus.IN_PROGRESS: [ProjectStatus.ON_HOLD, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED],
    ProjectStatus.ON_HOLD: [ProjectStatus.IN_PROGRESS, ProjectStatus.CANCELLED],
    ProjectStatus.COMPLETED: [],  # No transitions from completed
    ProjectStatus.CANCELLED: [],  # No transitions from cancelled
}

class ProjectPriority(str, PyEnum):
    """Enumeration of project priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Project(Base):
    """
    Project model representing client projects in the system.
    
    This model stores project information, including status, timelines,
    financial details, and relationships with clients and developers.
    
    Attributes:
        id (int): Primary key, auto-incrementing project ID
        title (str): Project title/name
        description (Text): Detailed project description
        status (ProjectStatus): Current project status
        priority (ProjectPriority): Project priority level
        start_date (datetime): Project start date
        end_date (datetime): Project target completion date
        actual_end_date (datetime): Actual project completion date
        budget (float): Project budget amount
        client_id (int): Foreign key to the client
        developer_id (int): Foreign key to the assigned developer
        created_at (datetime): Timestamp when project was created
        updated_at (datetime): Timestamp when project was last updated
        
    Relationships:
        client: Associated client for this project
        developer: Developer assigned to this project
        expenses: Project-related expenses
        payments: Payments received for this project
        milestones: Project milestones and deadlines
    """
    
    __tablename__ = "projects"
    
    def __init__(self, **kwargs):
        """Initialize Project with support for 'name' parameter mapping to 'title'."""
        # Handle backward compatibility: map 'name' to 'title'
        if 'name' in kwargs:
            kwargs['title'] = kwargs.pop('name')
        # Handle backward compatibility: map 'assigned_user_id' to 'developer_id'
        if 'assigned_user_id' in kwargs:
            kwargs['developer_id'] = kwargs.pop('assigned_user_id')
        super().__init__(**kwargs)
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, doc="Unique project identifier")
    
    # Project details
    title = Column(
        String(200), 
        nullable=False, 
        index=True,
        doc="Project title or name"
    )
    
    # Alias for backward compatibility with tests
    @property
    def name(self):
        """Alias for title field to maintain backward compatibility."""
        return self.title
    
    @name.setter
    def name(self, value):
        """Setter for name alias."""
        self.title = value
    
    @property
    def assigned_user_id(self):
        """Alias for developer_id field to maintain backward compatibility."""
        return self.developer_id
    
    @assigned_user_id.setter
    def assigned_user_id(self, value):
        """Setter for assigned_user_id alias."""
        self.developer_id = value
    description = Column(
        Text,
        doc="Detailed project description, requirements, and scope"
    )
    status = Column(
        String(50),
        nullable=False,
        default=ProjectStatus.PLANNING,
        doc="Current project status"
    )
    priority = Column(
        String(50),
        nullable=False,
        default=ProjectPriority.MEDIUM,
        doc="Project priority level"
    )
    
    # Dates and timeline
    start_date = Column(
        DateTime(timezone=True),
        doc="Project start date"
    )
    end_date = Column(
        DateTime(timezone=True),
        doc="Target project completion date"
    )
    actual_end_date = Column(
        DateTime(timezone=True),
        doc="Actual date when project was completed"
    )
    
    # Financial information
    budget = Column(
        Float,
        nullable=False,
        default=0.0,
        doc="Project budget amount"
    )
    hourly_rate = Column(
        Float,
        doc="Hourly rate for billing (if applicable)"
    )
    
    # Foreign keys
    client_id = Column(
        Integer, 
        ForeignKey("clients.id"), 
        nullable=False,
        index=True,
        doc="ID of the client this project belongs to"
    )
    developer_id = Column(
        Integer, 
        ForeignKey("users.id"),
        index=True,
        doc="ID of the developer assigned to this project"
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        doc="Timestamp when the project was created"
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        doc="Timestamp when the project was last updated"
    )
    
    # Relationships
    client = relationship(
        "Client", 
        back_populates="projects",
        doc="Client associated with this project"
    )
    developer = relationship(
        "User", 
        back_populates="assigned_projects",
        doc="Developer assigned to this project"
    )
    expenses = relationship(
        "Expense", 
        back_populates="linked_project",
        cascade="all, delete-orphan",
        doc="Expenses associated with this project"
    )
    payments = relationship(
        "Payment", 
        back_populates="project",
        cascade="all, delete-orphan",
        doc="Payments received for this project"
    )
    milestones = relationship(
        "ProjectMilestone",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectMilestone.due_date"
    )
    invoices = relationship(
        "Invoice",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of the Project object."""
        return f"<Project(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation of the Project object."""
        return f"{self.title} ({self.status})"
    
    @property
    def is_overdue(self) -> bool:
        """
        Check if the project is overdue.
        
        Returns:
            bool: True if project end date has passed and status is not completed
        """
        if not self.end_date:
            return False
        return (
            datetime.now() > self.end_date and 
            self.status not in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]
        )
    
    @property
    def total_expenses(self) -> float:
        """
        Calculate total expenses for this project.
        
        Returns:
            float: Sum of all expense amounts
        """
        return sum(expense.amount for expense in self.expenses)
    
    @property
    def total_payments(self) -> float:
        """
        Calculate total payments received for this project.
        
        Returns:
            float: Sum of all payment amounts
        """
        return sum(payment.amount for payment in self.payments)
    
    @property
    def profit_margin(self) -> float:
        """
        Calculate project profit margin.
        
        Returns:
            float: Profit margin as a percentage
        """
        if not self.total_payments:
            return 0.0
        profit = self.total_payments - self.total_expenses
        return (profit / self.total_payments) * 100
