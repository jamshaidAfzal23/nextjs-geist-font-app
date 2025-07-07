import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to allow imports from the application
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

# Import necessary modules
from backend_restructured.app.core.database import Base
from backend_restructured.app.models.user_model import User

# Create an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Import all models to ensure they are registered with Base.metadata
from backend_restructured.app.models import user_model, client_model, project_model, financial_model
from backend_restructured.app.models import client_note_model, client_history_model, project_milestone_model
from backend_restructured.app.models import api_key_model, user_preference_model

# Create all tables
Base.metadata.create_all(bind=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Create test admin user
from backend_restructured.app.core.security import hash_password
admin_user = User(
    email="admin@example.com",
    full_name="Admin User",
    role="admin",
    hashed_password=hash_password("admin123")
)
session.add(admin_user)

# Create test regular user
regular_user = User(
    email="user@example.com",
    full_name="Regular User",
    role="user",
    hashed_password=hash_password("user123")
)
session.add(regular_user)

session.commit()

print("Database tables created and seeded with test data.")

# Run the test
pytest.main(["backend_restructured/tests/test_user_endpoints.py::test_get_users", "-vv"])