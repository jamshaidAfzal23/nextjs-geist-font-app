"""
Client History schemas for the Smart CRM SaaS application.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ClientHistoryBase(BaseModel):
    client_id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    action: str = Field(..., example="Client created")
    details: Optional[str] = Field(None, example="New client Acme Corp added to the system.")

class ClientHistoryCreate(ClientHistoryBase):
    pass

class ClientHistoryResponse(ClientHistoryBase):
    id: int = Field(..., example=1)
    timestamp: datetime = Field(..., example="2023-01-01T12:00:00Z")

    class Config:
        from_attributes = True
