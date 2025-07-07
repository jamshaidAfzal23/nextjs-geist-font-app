"""Tests for database models."""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user_model import User
from app.models.client_model import Client
from app.models.project_model import Project
from app.models.financial_model import Invoice, Payment
from app.models.client_note_model import ClientNote
from app.models.client_history_model import ClientHistory

@pytest.mark.asyncio
def test_user_model(db_session: Session):
    """Test User model creation and relationships."""
    # Create a test user
    user = User(
        email="modeltest@example.com",
        hashed_password="hashed_password",
        full_name="Model Test User",
        role="user"
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Verify user was created with correct attributes
    assert user.id is not None
    assert user.email == "modeltest@example.com"
    assert user.full_name == "Model Test User"
    assert user.role == "user"
    assert user.hashed_password == "hashed_password"
    assert user.created_at is not None
    
    # Test user-client relationship
    client = Client(
        company_name="Model Test Client",
        contact_person_name="Test Contact",
        email="modelclient@example.com",
        assigned_user_id=user.id
    )
    
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    await db_session.refresh(user)
    
    # Get clients assigned to user
    result = await db_session.execute(user.clients.statement)
    user_clients = result.scalars().all()
    
    assert len(user_clients) == 1
    assert user_clients[0].company_name == "Model Test Client"

@pytest.mark.asyncio
def test_client_model(db_session: Session):
    """Test Client model creation and relationships."""
    # Create a test user first
    user = User(
        email="clientmodeltest@example.com",
        hashed_password="hashed_password",
        full_name="Client Model Test User",
        role="user"
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create a test client
    client = Client(
        company_name="Client Model Test",
        contact_person_name="Test Contact",
        email="clientmodel@example.com",
        phone_number="555-123-4567",
        address="123 Test St, Test City",
        industry="Technology",
        platform_preference="web",
        category="enterprise",
        general_notes="Test notes",
        assigned_user_id=user.id
    )
    
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    
    # Verify client was created with correct attributes
    assert client.id is not None
    assert client.company_name == "Client Model Test"
    assert client.contact_person_name == "Test Contact"
    assert client.email == "clientmodel@example.com"
    assert client.industry == "Technology"
    assert client.assigned_user_id == user.id
    assert client.created_at is not None
    
    # Test client-project relationship
    project = Project(
        name="Client Model Test Project",
        description="Test project for client model",
        client_id=client.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status="active",
        budget=10000.0,
        assigned_user_id=user.id
    )
    
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    await db_session.refresh(client)
    
    # Get projects for client
    result = await db_session.execute(client.projects.statement)
    client_projects = result.scalars().all()
    
    assert len(client_projects) == 1
    assert client_projects[0].name == "Client Model Test Project"
    
    # Test total_project_value property
    assert client.total_project_value == 10000.0
    
    # Test active_projects_count property
    assert client.active_projects_count == 1

@pytest.mark.asyncio
def test_project_model(db_session: Session):
    """Test Project model creation and relationships."""
    # Create a test user and client first
    user = User(
        email="projectmodeltest@example.com",
        hashed_password="hashed_password",
        full_name="Project Model Test User",
        role="user"
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    client = Client(
        company_name="Project Model Test Client",
        contact_person_name="Test Contact",
        email="projectclient@example.com",
        assigned_user_id=user.id
    )
    
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    
    # Create a test project
    project = Project(
        name="Project Model Test",
        description="Test project for project model",
        client_id=client.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status="active",
        budget=15000.0,
        assigned_user_id=user.id
    )
    
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # Verify project was created with correct attributes
    assert project.id is not None
    assert project.name == "Project Model Test"
    assert project.description == "Test project for project model"
    assert project.client_id == client.id
    assert project.status == "active"
    assert project.budget == 15000.0
    assert project.assigned_user_id == user.id
    assert project.created_at is not None
    
    # Test project-invoice relationship
    invoice = Invoice(
        client_id=client.id,
        project_id=project.id,
        amount=5000.0,
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        status="pending",
        description="Test invoice for project model"
    )
    
    db_session.add(invoice)
    await db_session.commit()
    await db_session.refresh(invoice)
    await db_session.refresh(project)
    
    # Get invoices for project
    result = await db_session.execute(project.invoices.statement)
    project_invoices = result.scalars().all()
    
    assert len(project_invoices) == 1
    assert project_invoices[0].amount == 5000.0

@pytest.mark.asyncio
def test_invoice_and_payment_models(db_session: Session):
    """Test Invoice and Payment models creation and relationships."""
    # Create test user, client, and project first
    user = User(
        email="invoicemodeltest@example.com",
        hashed_password="hashed_password",
        full_name="Invoice Model Test User",
        role="user"
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    client = Client(
        company_name="Invoice Model Test Client",
        contact_person_name="Test Contact",
        email="invoiceclient@example.com",
        assigned_user_id=user.id
    )
    
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    
    project = Project(
        name="Invoice Model Test Project",
        description="Test project for invoice model",
        client_id=client.id,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30),
        status="active",
        budget=20000.0,
        assigned_user_id=user.id
    )
    
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    # Create a test invoice
    invoice = Invoice(
        client_id=client.id,
        project_id=project.id,
        amount=10000.0,
        issue_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=30),
        status="pending",
        description="Test invoice for invoice model"
    )
    
    db_session.add(invoice)
    await db_session.commit()
    await db_session.refresh(invoice)
    
    # Verify invoice was created with correct attributes
    assert invoice.id is not None
    assert invoice.client_id == client.id
    assert invoice.project_id == project.id
    assert invoice.amount == 10000.0
    assert invoice.status == "pending"
    assert invoice.created_at is not None
    
    # Create a test payment
    payment = Payment(
        invoice_id=invoice.id,
        amount=5000.0,
        payment_date=datetime.now(),
        payment_method="credit_card",
        transaction_id="txn_test_model",
        notes="Test payment for invoice model"
    )
    
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)
    await db_session.refresh(invoice)
    
    # Verify payment was created with correct attributes
    assert payment.id is not None
    assert payment.invoice_id == invoice.id
    assert payment.amount == 5000.0
    assert payment.payment_method == "credit_card"
    assert payment.transaction_id == "txn_test_model"
    assert payment.created_at is not None
    
    # Get payments for invoice
    result = await db_session.execute(invoice.payments.statement)
    invoice_payments = result.scalars().all()
    
    assert len(invoice_payments) == 1
    assert invoice_payments[0].amount == 5000.0
    
    # Test paid_amount property
    assert invoice.paid_amount == 5000.0
    
    # Test remaining_amount property
    assert invoice.remaining_amount == 5000.0

@pytest.mark.asyncio
def test_client_note_model(db_session: Session):
    """Test ClientNote model creation and relationships."""
    # Create test user and client first
    user = User(
        email="notemodeltest@example.com",
        hashed_password="hashed_password",
        full_name="Note Model Test User",
        role="user"
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    client = Client(
        company_name="Note Model Test Client",
        contact_person_name="Test Contact",
        email="noteclient@example.com",
        assigned_user_id=user.id
    )
    
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    
    # Create a test note
    note = ClientNote(
        client_id=client.id,
        user_id=user.id,
        content="Test note for client note model"
    )
    
    db_session.add(note)
    await db_session.commit()
    await db_session.refresh(note)
    
    # Verify note was created with correct attributes
    assert note.id is not None
    assert note.client_id == client.id
    assert note.user_id == user.id
    assert note.content == "Test note for client note model"
    assert note.created_at is not None
    
    # Get notes for client
    result = await db_session.execute(client.notes.statement)
    client_notes = result.scalars().all()
    
    assert len(client_notes) == 1
    assert client_notes[0].content == "Test note for client note model"

@pytest.mark.asyncio
def test_client_history_model(db_session: Session):
    """Test ClientHistory model creation and relationships."""
    # Create test user and client first
    user = User(
        email="historymodeltest@example.com",
        hashed_password="hashed_password",
        full_name="History Model Test User",
        role="user"
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    client = Client(
        company_name="History Model Test Client",
        contact_person_name="Test Contact",
        email="historyclient@example.com",
        assigned_user_id=user.id
    )
    
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    
    # Create a test history entry
    history = ClientHistory(
        client_id=client.id,
        user_id=user.id,
        action="created",
        details="Client created for history model test"
    )
    
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)
    
    # Verify history was created with correct attributes
    assert history.id is not None
    assert history.client_id == client.id
    assert history.user_id == user.id
    assert history.action == "created"
    assert history.details == "Client created for history model test"
    assert history.timestamp is not None
    
    # Get history for client
    result = await db_session.execute(client.history.statement)
    client_history = result.scalars().all()
    
    assert len(client_history) == 1
    assert client_history[0].action == "created"