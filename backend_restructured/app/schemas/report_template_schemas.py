"""
Report Template schemas for the Smart CRM SaaS application.
"""

from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ReportTemplateBase(BaseModel):
    name: str
    template_type: str
    template_content: Dict

class ReportTemplateCreate(ReportTemplateBase):
    pass

class ReportTemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_type: Optional[str] = None
    template_content: Optional[Dict] = None

class ReportTemplateResponse(ReportTemplateBase):
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2023-01-01T10:00:00Z")

    class Config:
        from_attributes = True
