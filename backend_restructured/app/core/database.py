"""
Database configuration and session management for Smart CRM SaaS.
This module handles SQLAlchemy database setup, session management, and provides
database dependency injection for FastAPI endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

# Create SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed only for SQLite
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

def get_database_session() -> Generator[Session, None, None]:
    """
    Dependency function that provides database session to FastAPI endpoints.
    
    This function creates a new database session for each request and ensures
    it's properly closed after the request is completed.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_database_session)):
            return db.query(User).all()
    """
    database_session = SessionLocal()
    try:
        yield database_session
    finally:
        database_session.close()

def create_database_tables():
    """
    Create all database tables based on the defined models.
    
    This function should be called during application startup to ensure
    all required tables exist in the database.
    """
    Base.metadata.create_all(bind=engine)

def check_database_connection():
    """
    Checks if the database connection is alive.
    """
    try:
        with engine.connect() as connection:
            return True
    except Exception:
        return False
