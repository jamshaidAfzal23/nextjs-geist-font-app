"""
Client Note schemas for the Smart CRM SaaS application.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ClientNoteBase(BaseModel):
    content: str

class ClientNoteCreate(ClientNoteBase):
    client_id: int = Field(..., example=1)

class ClientNoteResponse(ClientNoteBase):
    id: int = Field(..., example=1)
    client_id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2023-01-01T10:00:00Z")

    class Config:
        from_attributes = True
