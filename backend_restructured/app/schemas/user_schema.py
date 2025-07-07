"""User-related Pydantic schemas."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, constr

class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    full_name: constr(min_length=1, max_length=100)
    role: constr(regex='^(user|admin)$')

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    role: Optional[constr(regex='^(user|admin)$')] = None
    password: Optional[constr(min_length=8)] = None

class UserPreferences(BaseModel):
    """Schema for user preferences."""
    theme: Optional[str] = "light"
    notifications_enabled: Optional[bool] = True
    dashboard_layout: Optional[str] = "default"

class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True