"""
Configuration settings for the Smart CRM SaaS application.
This module contains all the configuration variables used throughout the application.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings class that loads configuration from environment variables.
    
    Attributes:
        PROJECT_NAME (str): Name of the project
        VERSION (str): API version
        API_V1_STR (str): API version prefix for URLs
        DATABASE_URL (str): SQLite database URL
        CORS_ORIGINS (list): List of allowed origins for CORS
    """
    PROJECT_NAME: str = "Smart CRM SaaS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./smartcrm.db"
    CORS_ORIGINS: list = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # FastAPI backend
    ]
    OPENAI_API_KEY: str = "your-openai-api-key-here" # Replace with your actual OpenAI API key
    SENDGRID_API_KEY: str = "your-sendgrid-api-key-here"
    MAIL_FROM_EMAIL: str = "your-verified-sender-email@example.com"

    class Config:
        case_sensitive = True

# Create global settings object
settings = Settings()
