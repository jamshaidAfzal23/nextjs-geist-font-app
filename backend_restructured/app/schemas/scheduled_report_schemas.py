"""
Scheduled Report schemas for the Smart CRM SaaS application.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class ScheduledReportBase(BaseModel):
    report_name: str
    report_type: str
    schedule_interval: str
    next_run_at: datetime
    recipients: str
    is_active: Optional[bool] = True

class ScheduledReportCreate(ScheduledReportBase):
    pass

class ScheduledReportUpdate(BaseModel):
    report_name: Optional[str] = None
    report_type: Optional[str] = None
    schedule_interval: Optional[str] = None
    next_run_at: Optional[datetime] = None
    recipients: Optional[str] = None
    is_active: Optional[bool] = None

class ScheduledReportResponse(ScheduledReportBase):
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    last_run_at: Optional[datetime] = Field(None, example="2023-07-03T09:00:00Z")
    created_at: datetime = Field(..., example="2023-07-01T10:00:00Z")

    class Config:
        from_attributes = True
