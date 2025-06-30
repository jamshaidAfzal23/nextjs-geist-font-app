"""
Project schemas for Smart CRM SaaS application.
This module defines Pydantic models for project data validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from ..models.project_model import ProjectStatus, ProjectPriority

class ProjectBase(BaseModel):
    """
    Base project schema with common fields.
    
    Attributes:
        title (str): Project title or name
        description (str): Detailed project description
        status (ProjectStatus): Current project status
        priority (ProjectPriority): Project priority level
        start_date (datetime): Project start date
        end_date (datetime): Target completion date
        budget (float): Project budget amount
        hourly_rate (float): Hourly billing rate
    """
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Project title or name"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Detailed project description and requirements"
    )
    status: ProjectStatus = Field(
        default=ProjectStatus.PLANNING,
        description="Current project status"
    )
    priority: ProjectPriority = Field(
        default=ProjectPriority.MEDIUM,
        description="Project priority level"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Project start date"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Target project completion date"
    )
    budget: float = Field(
        default=0.0,
        ge=0,
        description="Project budget amount"
    )
    hourly_rate: Optional[float] = Field(
        None,
        ge=0,
        description="Hourly rate for billing (if applicable)"
    )
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date."""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v

class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.
    
    Includes client_id and developer_id for project assignment.
    """
    client_id: int = Field(
        ...,
        description="ID of the client this project belongs to"
    )
    developer_id: Optional[int] = Field(
        None,
        description="ID of the developer assigned to this project"
    )

class ProjectUpdate(BaseModel):
    """
    Schema for updating project information.
    
    All fields are optional for partial updates.
    """
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        description="Updated project title"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Updated project description"
    )
    status: Optional[ProjectStatus] = Field(
        None,
        description="Updated project status"
    )
    priority: Optional[ProjectPriority] = Field(
        None,
        description="Updated project priority"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Updated start date"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Updated end date"
    )
    actual_end_date: Optional[datetime] = Field(
        None,
        description="Actual completion date"
    )
    budget: Optional[float] = Field(
        None,
        ge=0,
        description="Updated budget amount"
    )
    hourly_rate: Optional[float] = Field(
        None,
        ge=0,
        description="Updated hourly rate"
    )
    developer_id: Optional[int] = Field(
        None,
        description="Updated assigned developer ID"
    )

class ProjectResponse(ProjectBase):
    """
    Schema for project data in API responses.
    
    Includes all project information with relationships and computed fields.
    """
    id: int = Field(..., description="Unique project identifier")
    client_id: int = Field(..., description="Associated client ID")
    developer_id: Optional[int] = Field(None, description="Assigned developer ID")
    actual_end_date: Optional[datetime] = Field(None, description="Actual completion date")
    created_at: datetime = Field(..., description="When the project was created")
    updated_at: datetime = Field(..., description="When the project was last updated")
    
    # Computed fields
    is_overdue: Optional[bool] = Field(
        None,
        description="Whether the project is past its end date"
    )
    total_expenses: Optional[float] = Field(
        None,
        description="Total expenses for this project"
    )
    total_payments: Optional[float] = Field(
        None,
        description="Total payments received for this project"
    )
    profit_margin: Optional[float] = Field(
        None,
        description="Profit margin as a percentage"
    )
    
    # Related data (optional, loaded when needed)
    client_name: Optional[str] = Field(
        None,
        description="Name of the associated client"
    )
    developer_name: Optional[str] = Field(
        None,
        description="Name of the assigned developer"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProjectListResponse(BaseModel):
    """
    Schema for paginated project list responses.
    
    Contains list of projects with pagination metadata.
    """
    projects: List[ProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of projects per page")

class ProjectSummary(BaseModel):
    """
    Schema for project summary information.
    
    Contains essential project information for dashboards and quick references.
    """
    id: int = Field(..., description="Project ID")
    title: str = Field(..., description="Project title")
    status: ProjectStatus = Field(..., description="Project status")
    priority: ProjectPriority = Field(..., description="Project priority")
    client_name: str = Field(..., description="Client name")
    budget: float = Field(..., description="Project budget")
    progress_percentage: Optional[float] = Field(
        None,
        description="Project completion percentage"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

class ProjectSearchFilters(BaseModel):
    """
    Schema for project search and filtering parameters.
    
    Contains optional filters for project queries.
    """
    search_term: Optional[str] = Field(
        None,
        max_length=100,
        description="Search term for project title or description"
    )
    status: Optional[ProjectStatus] = Field(
        None,
        description="Filter by project status"
    )
    priority: Optional[ProjectPriority] = Field(
        None,
        description="Filter by project priority"
    )
    client_id: Optional[int] = Field(
        None,
        description="Filter by client ID"
    )
    developer_id: Optional[int] = Field(
        None,
        description="Filter by assigned developer"
    )
    is_overdue: Optional[bool] = Field(
        None,
        description="Filter overdue projects"
    )
    budget_min: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum budget amount"
    )
    budget_max: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum budget amount"
    )
    start_date_after: Optional[datetime] = Field(
        None,
        description="Filter projects starting after this date"
    )
    end_date_before: Optional[datetime] = Field(
        None,
        description="Filter projects ending before this date"
    )

class ProjectStats(BaseModel):
    """
    Schema for project statistics and analytics.
    
    Contains aggregated data about projects.
    """
    total_projects: int = Field(..., description="Total number of projects")
    projects_by_status: dict = Field(..., description="Project count by status")
    projects_by_priority: dict = Field(..., description="Project count by priority")
    overdue_projects: int = Field(..., description="Number of overdue projects")
    total_budget: float = Field(..., description="Sum of all project budgets")
    average_project_duration: Optional[float] = Field(
        None,
        description="Average project duration in days"
    )
    completion_rate: float = Field(..., description="Percentage of completed projects")
    
class ProjectMilestone(BaseModel):
    """
    Schema for project milestones and deadlines.
    
    Represents important dates and deliverables within a project.
    """
    id: Optional[int] = Field(None, description="Milestone ID")
    project_id: int = Field(..., description="Associated project ID")
    title: str = Field(..., max_length=200, description="Milestone title")
    description: Optional[str] = Field(None, description="Milestone description")
    due_date: datetime = Field(..., description="Milestone due date")
    is_completed: bool = Field(default=False, description="Whether milestone is completed")
    completion_date: Optional[datetime] = Field(None, description="When milestone was completed")
