"""
Automated Task schemas for the Smart CRM SaaS application.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AutomatedTaskBase(BaseModel):
    task_type: str
    scheduled_time: datetime
    target_id: Optional[int] = None
    target_type: Optional[str] = None
    details: Optional[str] = None

class AutomatedTaskCreate(AutomatedTaskBase):
    pass

class AutomatedTaskUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    is_completed: Optional[bool] = None
    details: Optional[str] = None

class AutomatedTaskResponse(AutomatedTaskBase):
    id: int = Field(..., example=1)
    is_completed: bool = Field(..., example=False)
    completed_at: Optional[datetime] = Field(None, example="2023-07-15T09:30:00Z")
    created_by_id: int = Field(..., example=1)

    class Config:
        from_attributes = True
