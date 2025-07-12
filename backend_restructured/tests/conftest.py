"""Test configuration for the Smart CRM SaaS backend."""

import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta

# Add the parent directory to sys.path to allow imports from the application
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Now we can import from the app module
from main import app
from app.core.database import get_database_session, Base
from app.models.user_model import User
from app.auth.auth import hash_password, create_access_token

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create a synchronous SQLite engine for testing."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(engine):
    """Create a fresh database session for a test."""
    # Import all models to ensure they are registered with Base.metadata
    from app.models import user_model, client_model, project_model, financial_model
    from app.models import client_note_model, client_history_model, project_milestone_model
    from app.models import api_key_model, user_preference_model
    
    # Create all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_database_session] = override_get_db
    
    yield session
    
    # Clean up
    session.rollback()
    Base.metadata.drop_all(bind=engine)
    session.close()
    app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def create_tables(engine):
    """Create all tables in the database."""
    # Import all models to ensure they are registered with Base.metadata
    from app.models import user_model, client_model, project_model, financial_model
    from app.models import client_note_model, client_history_model, project_milestone_model
    from app.models import api_key_model, user_preference_model
    
    # Create all tables
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def seed_database(db_session: Session):
    """Seed the database with test data."""
    # Import models
    from app.models.client_model import Client
    from app.models.project_model import Project
    
    # Create test users
    admin_user = User(
        email="admin@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin_password"
        full_name="Admin User",
        role="admin",
        is_admin=True
    )
    
    regular_user = User(
        email="user@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin_password"
        full_name="Regular User",
        role="user",
        is_admin=False
    )
    
    db_session.add_all([admin_user, regular_user])
    db_session.commit()
    db_session.refresh(admin_user)
    db_session.refresh(regular_user)
    
    # Create test clients
    test_client_1 = Client(
        id=1,
        company_name="Test Company 1",
        contact_person_name="John Doe",
        email="john@testcompany1.com",
        phone_number="1234567890",
        address="123 Test St, Test City, TC 12345",
        industry="Technology",
        platform_preference="Web",
        general_notes="Test client for automated testing",
        assigned_user_id=admin_user.id
    )
    
    test_client_2 = Client(
        id=2,
        company_name="Test Company 2",
        contact_person_name="Jane Smith",
        email="jane@testcompany2.com",
        phone_number="0987654321",
        address="456 Test Ave, Test City, TC 54321",
        industry="Finance",
        platform_preference="Mobile",
        general_notes="Another test client",
        assigned_user_id=regular_user.id
    )
    
    db_session.add_all([test_client_1, test_client_2])
    db_session.commit()
    db_session.refresh(test_client_1)
    db_session.refresh(test_client_2)
    
    # Create test financial data
    from app.models.financial_model import Invoice, Payment
    from datetime import datetime, timedelta
    
    # Create test invoices
    test_invoice_1 = Invoice(
        id=1,
        client_id=test_client_1.id,
        amount=5000.0,
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        status="sent",
        description="Test invoice 1",
        items='[]'  # JSON string instead of Python list
    )
    
    test_invoice_2 = Invoice(
        id=2,
        client_id=test_client_2.id,
        amount=3000.0,
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=15),
        status="paid",
        description="Test invoice 2",
        items='[]'  # JSON string instead of Python list
    )
    
    db_session.add_all([test_invoice_1, test_invoice_2])
    db_session.commit()
    db_session.refresh(test_invoice_1)
    db_session.refresh(test_invoice_2)
    
    # Create test payments
    test_payment_1 = Payment(
        id=1,
        invoice_id=test_invoice_2.id,
        client_id=test_client_2.id,
        project_id=1,  # Add project_id to avoid validation errors
        amount=3000.0,
        payment_date=datetime.now(),
        payment_method="credit_card",
        transaction_id="txn_test_123"
    )
    
    db_session.add(test_payment_1)
    db_session.commit()
    db_session.refresh(test_payment_1)
    
    return {
        "admin_user": admin_user,
        "regular_user": regular_user,
        "test_client_1": test_client_1,
        "test_client_2": test_client_2,
        "test_invoice_1": test_invoice_1,
        "test_invoice_2": test_invoice_2,
        "test_payment_1": test_payment_1
    }

@pytest.fixture
def admin_token():
    """Create a JWT token for the admin user."""
    return create_access_token(
        data={"sub": "admin@example.com", "role": "admin"},
        expires_delta=timedelta(minutes=30)
    )

@pytest.fixture
def user_token():
    """Create a JWT token for a regular user."""
    return create_access_token(
        data={"sub": "user@example.com", "role": "user"},
        expires_delta=timedelta(minutes=30)
    )

@pytest.fixture
def admin_headers(admin_token):
    """Create headers with admin JWT token."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token):
    """Create headers with user JWT token."""
    return {"Authorization": f"Bearer {user_token}"}