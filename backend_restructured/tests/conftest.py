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
from app.core.database import Base, get_database_session
from app.models.user_model import User
from app.auth.auth import hash_password, create_access_token
from fastapi.testclient import TestClient
from app.core.config import settings
from app.core.database import engine as prod_engine

# Use a file-based SQLite database for testing to ensure persistence across connections
TEST_DATABASE_URL = "sqlite:///test.db"

@pytest.fixture(scope="session")
def engine():
    """Create a synchronous SQLite engine for testing."""
    # Remove the test.db file if it exists to ensure a clean state
    if os.path.exists("test.db"):
        os.remove("test.db")
    test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
    # Import all models to ensure they are registered with Base.metadata
    from app.models import user_model, client_model, project_model, financial_model
    from app.models import client_note_model, client_history_model, project_milestone_model
    from app.models import api_key_model, user_preference_model
    
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=test_engine)
    # Import specific model classes to ensure they're registered
    from app.models.user_model import User
    from app.models.client_model import Client
    from app.models.project_model import Project
    from app.models.financial_model import Payment, Invoice, Expense
    from app.models.client_note_model import ClientNote
    from app.models.client_history_model import ClientHistory
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    # Clean up the test.db file after tests
    if os.path.exists("test.db"):
        os.remove("test.db")

@pytest.fixture(autouse=True)
def setup_test_database(db_session):
    """Setup test database before each test."""
    # Clear all tables before each test
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    
    try:
        yield
    finally:
        db_session.rollback()

@pytest.fixture
def db_session(engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(autouse=True)
def override_dependency(db_session):
    """Override the database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session closure is handled by db_session fixture
    from main import app
    app.dependency_overrides[get_database_session] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def create_tables(engine):
    """Create all tables in the database."""
    # Import all models to ensure they are registered with Base.metadata
    from app.models import user_model, client_model, project_model, financial_model
    from app.models import client_note_model, client_history_model, project_milestone_model
    from app.models import api_key_model, user_preference_model
    
    # Import specific model classes to ensure they're registered
    from app.models.user_model import User
    from app.models.client_model import Client
    from app.models.project_model import Project
    from app.models.financial_model import Payment, Invoice, Expense
    from app.models.client_note_model import ClientNote
    from app.models.client_history_model import ClientHistory
    
    # Create all tables
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def seed_database(db_session: Session):
    """Seed the database with test data."""
    # Create test users
    admin_user = User(
        email="admin@example.com",
        hashed_password=hash_password("admin_password"),
        full_name="Admin User",
        role="admin",
        is_admin=True,
        is_active=True
    )
    
    regular_user = User(
        email=f"user_{datetime.now().timestamp()}@example.com",
        hashed_password=hash_password("user_password"),
        full_name="Regular User",
        role="user",
        is_admin=False
    )
    
    db_session.add_all([admin_user, regular_user])
    db_session.commit()
    db_session.refresh(admin_user)
    db_session.refresh(regular_user)

    # Create user preferences
    from app.models.user_preference_model import UserPreference
    
    admin_preferences = UserPreference(
        user_id=admin_user.id,
        theme="light",
        notifications_enabled=True,
        dashboard_layout="default"
    )

    user_preferences = UserPreference(
        user_id=regular_user.id,
        theme="dark",
        notifications_enabled=True,
        dashboard_layout="compact"
    )

    db_session.add_all([admin_preferences, user_preferences])
    db_session.commit()
    
    # Create test clients
    from app.models.client_model import Client
    
    test_client_1 = Client(
        company_name=f"Test Company 1 {datetime.now().timestamp()}",
        contact_person_name="John Doe",
        email=f"john_{datetime.now().timestamp()}@testcompany1.com",
        phone_number="1234567890",
        address="123 Test St, Test City, TC 12345",
        industry="Technology",
        platform_preference="Web",
        general_notes="Test client for automated testing",
        assigned_user_id=admin_user.id
    )
    
    test_client_2 = Client(
        company_name=f"Test Company 2 {datetime.now().timestamp()}",
        contact_person_name="Jane Smith",
        email=f"jane_{datetime.now().timestamp()}@testcompany2.com",
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
        project_id=1,  # Add project_id field
        amount=5000.0,
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        status="sent",
        notes="Test invoice 1",  # Use notes instead of description
        items='[]'  # JSON string instead of Python list
    )
    
    test_invoice_2 = Invoice(
        id=2,
        client_id=test_client_2.id,
        project_id=1,  # Add project_id field
        amount=3000.0,
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=15),
        status="paid",
        notes="Test invoice 2",  # Use notes instead of description
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
        method="credit_card",  # Use method instead of payment_method
        transaction_id="txn_test_123",
        payment_gateway_id="gw_test_123"  # Add payment_gateway_id field
    )
    
    db_session.add(test_payment_1)
    db_session.commit()
    db_session.refresh(test_payment_1)
    
    return {
        "admin_user": admin_user,
        "regular_user": regular_user,
        "test_client_1": test_client_1,
        "test_client_2": test_client_2
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