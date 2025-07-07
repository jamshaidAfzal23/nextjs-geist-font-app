"""
Project Milestone schemas for the Smart CRM SaaS application.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectMilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime

class ProjectMilestoneCreate(ProjectMilestoneBase):
    project_id: int = Field(..., example=1)

class ProjectMilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

class ProjectMilestoneResponse(ProjectMilestoneBase):
    id: int = Field(..., example=1)
    project_id: int = Field(..., example=1)
    is_completed: bool = Field(..., example=False)
    completed_at: Optional[datetime] = Field(None, example="2023-07-29T16:00:00Z")

    class Config:
        from_attributes = True
