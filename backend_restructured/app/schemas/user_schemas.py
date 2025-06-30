"""
User schemas for Smart CRM SaaS application.
This module defines Pydantic models for user data validation and serialization.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """
    Base user schema with common fields.
    
    Attributes:
        full_name (str): User's full name (2-100 characters)
        email (EmailStr): Valid email address
        role (str): User role (admin, manager, developer, viewer)
    """
    full_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="User's full name"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address for authentication"
    )
    role: str = Field(
        default="user",
        description="User role determining access permissions"
    )
    
    @validator('role')
    def validate_role(cls, v):
        """Validate that role is one of the allowed values."""
        allowed_roles = ['admin', 'manager', 'developer', 'user', 'viewer']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    
    Includes password field for user registration.
    """
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)"
    )
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    
    All fields are optional for partial updates.
    """
    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Updated full name"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Updated email address"
    )
    role: Optional[str] = Field(
        None,
        description="Updated user role"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the user account is active"
    )
    
    @validator('role')
    def validate_role(cls, v):
        """Validate that role is one of the allowed values."""
        if v is not None:
            allowed_roles = ['admin', 'manager', 'developer', 'user', 'viewer']
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

class UserResponse(UserBase):
    """
    Schema for user data in API responses.
    
    Includes all user information except sensitive data like passwords.
    """
    id: int = Field(..., description="Unique user identifier")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user's email is verified")
    created_at: datetime = Field(..., description="When the user account was created")
    updated_at: datetime = Field(..., description="When the user account was last updated")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserLogin(BaseModel):
    """
    Schema for user login requests.
    
    Contains credentials for authentication.
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class UserToken(BaseModel):
    """
    Schema for authentication token response.
    
    Contains access token and user information.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user information")

class UserListResponse(BaseModel):
    """
    Schema for paginated user list responses.
    
    Contains list of users with pagination metadata.
    """
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of users per page")
    
class PasswordChange(BaseModel):
    """
    Schema for password change requests.
    
    Contains current and new password for validation.
    """
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (minimum 8 characters)"
    )
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
