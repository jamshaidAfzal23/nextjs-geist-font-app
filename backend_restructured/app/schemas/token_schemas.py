"""
Token schemas for Smart CRM SaaS application.
This module defines Pydantic models for token data validation and serialization.
"""

from pydantic import BaseModel, Field
from datetime import datetime

class Token(BaseModel):
    """
    Schema for authentication tokens.
    
    Attributes:
        access_token (str): JWT access token
        token_type (str): Token type (default: bearer)
        expires_at (datetime): Token expiration timestamp
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_at: datetime = Field(..., description="Token expiration timestamp")

class TokenData(BaseModel):
    """
    Schema for token payload data.
    
    Attributes:
        user_id (int): Authenticated user ID
        email (str): User's email address
    """
    user_id: int = Field(..., description="Authenticated user ID")
    email: str = Field(..., description="User's email address")
