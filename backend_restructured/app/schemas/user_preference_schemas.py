"""
User Preference schemas for the Smart CRM SaaS application.
"""

from pydantic import BaseModel
from typing import Optional

class UserPreferenceBase(BaseModel):
    theme: Optional[str] = "light"
    notifications_enabled: Optional[bool] = True

class UserPreferenceCreate(UserPreferenceBase):
    pass

class UserPreferenceUpdate(UserPreferenceBase):
    pass

class UserPreferenceResponse(UserPreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
