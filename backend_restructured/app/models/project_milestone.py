"""Project milestone model for tracking project progress."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from ..core.database import Base

class MilestoneStatus(str, Enum):
    """Enumeration for milestone status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"

class ProjectMilestone(Base):
    """Model for tracking project milestones and deliverables.
    
    This model helps track the progress of projects through defined milestones,
    each with its own status, due date, and completion criteria.
    
    Attributes:
        id (int): Primary key
        project_id (int): Foreign key to the project
        title (str): Title of the milestone
        description (Text): Detailed description of the milestone
        status (MilestoneStatus): Current status of the milestone
        due_date (datetime): When the milestone is due
        completed_date (datetime): When the milestone was completed
        completion_notes (Text): Notes about milestone completion
        created_at (datetime): When the milestone was created
        updated_at (datetime): When the milestone was last updated
    """
    
    __tablename__ = "project_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(
        String(200),
        nullable=False,
        doc="Title of the milestone"
    )
    description = Column(
        Text,
        nullable=True,
        doc="Detailed description of what needs to be achieved"
    )
    status = Column(
        SQLEnum(MilestoneStatus),
        nullable=False,
        default=MilestoneStatus.PENDING,
        doc="Current status of the milestone"
    )
    due_date = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="When this milestone is due"
    )
    completed_date = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When this milestone was completed"
    )
    completion_notes = Column(
        Text,
        nullable=True,
        doc="Notes about the completion of this milestone"
    )
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
    
    # Relationships
    project = relationship(
        "Project",
        back_populates="milestones",
        doc="The project this milestone belongs to"
    )
    
    def __repr__(self) -> str:
        """String representation of the ProjectMilestone object."""
        return f"<ProjectMilestone(id={self.id}, project_id={self.project_id}, title='{self.title}')>"
    
    @property
    def is_completed(self) -> bool:
        """Check if the milestone is completed.
        
        Returns:
            bool: True if status is COMPLETED, False otherwise
        """
        return self.status == MilestoneStatus.COMPLETED
    
    @property
    def is_overdue(self) -> bool:
        """Check if the milestone is overdue.
        
        Returns:
            bool: True if due date has passed and status is not COMPLETED
        """
        return (
            self.due_date < func.now() and
            self.status not in [MilestoneStatus.COMPLETED, MilestoneStatus.CANCELLED]
        )