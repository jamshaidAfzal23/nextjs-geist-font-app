"""
Notification schemas for the Smart CRM SaaS application.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: str

class NotificationCreate(NotificationBase):
    user_id: int = Field(..., example=1)

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    is_read: bool = Field(..., example=False)
    created_at: datetime = Field(..., example="2023-01-01T10:00:00Z")

    class Config:
        from_attributes = True
