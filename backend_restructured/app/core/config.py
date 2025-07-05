"""
Configuration settings for the Smart CRM SaaS application.
This module contains all the configuration variables used throughout the application.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings class that loads configuration from environment variables.
    """
    PROJECT_NAME: str = "Smart CRM SaaS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./smartcrm.db"
    
    # Authentication
    SECRET_KEY: str = "key here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    
    # API Keys
    OPENAI_API_KEY: str = "key here"
    SENDGRID_API_KEY: str = "key here"
    MAIL_FROM_EMAIL: str = "your-verified-sender-email@example.com"
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000"
    ]


    class Config:
        case_sensitive = True

# Create global settings object
settings = Settings()
