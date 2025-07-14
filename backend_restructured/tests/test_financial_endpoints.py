"""Comprehensive tests for financial endpoints (invoices and payments)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from main import app

# Invoice Tests
def test_get_invoices(db_session, seed_database, admin_headers):
    """Test getting all invoices."""
    client = TestClient(app)
    response = client.get("/api/v1/invoices/", headers=admin_headers)
    assert response.status_code == 200
    assert "invoices" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["invoices"], list)

def test_get_invoice_by_id(db_session, seed_database, admin_headers):
    """Test getting a specific invoice by ID."""
    client = TestClient(app)
    response = client.get("/api/v1/invoices/1", headers=admin_headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert "client_id" in response.json()
    assert "amount" in response.json()
    assert "status" in response.json()

def test_create_invoice(test_client, seed_database, admin_headers):
    """Test creating a new invoice."""
    invoice_data = {
        "invoice_number": "INV-TEST-001",
        "client_id": seed_database["test_client_1"].id,
        "amount": 5000.0,
        "issue_date": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "status": "sent",
        "notes": "Test invoice",
        "items": [
            {"description": "Service 1", "quantity": 1, "unit_price": 3000.0},
            {"description": "Service 2", "quantity": 2, "unit_price": 1000.0}
        ]
    }
    response = test_client.post("/api/v1/invoices/", json=invoice_data, headers=admin_headers)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["client_id"] == invoice_data["client_id"]
    assert response.json()["amount"] == invoice_data["amount"]
    assert response.json()["status"] == invoice_data["status"]
    assert "items" in response.json()
    assert len(response.json()["items"]) == 2

def test_update_invoice(db_session, seed_database, admin_headers):
    """Test updating an invoice."""
    update_data = {
        "status": "paid",
        "paid_date": datetime.now().isoformat()
    }
    client = TestClient(app)
    response = client.put("/api/v1/invoices/1", json=update_data, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == update_data["status"]
    assert "paid_date" in response.json()

def test_delete_invoice(db_session, seed_database, admin_headers):
    """Test deleting an invoice."""
    client = TestClient(app)
    response = client.delete("/api/v1/invoices/1", headers=admin_headers)
    assert response.status_code == 204

def test_get_client_invoices(db_session, seed_database, admin_headers):
    """Test getting all invoices for a specific client."""
    client = TestClient(app)
    response = client.get(f"/api/v1/invoices/client/{seed_database['test_client_1'].id}", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for invoice in response.json():
        assert invoice["client_id"] == seed_database['test_client_1'].id

def test_invoice_stats(db_session, seed_database, admin_headers):
    """Test getting invoice statistics."""
    client = TestClient(app)
    response = client.get("/api/v1/invoices/stats", headers=admin_headers)
    assert response.status_code == 200
    assert "total_invoices" in response.json()
    assert "total_amount" in response.json()

# Payment Tests
def test_get_payments(db_session, seed_database, admin_headers):
    """Test getting all payments."""
    client = TestClient(app)
    response = client.get("/api/v1/payments/", headers=admin_headers)
    assert response.status_code == 200
    assert "payments" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["payments"], list)

def test_get_payment_by_id(db_session, seed_database, admin_headers):
    """Test getting a specific payment by ID."""
    client = TestClient(app)
    response = client.get("/api/v1/payments/1", headers=admin_headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert "invoice_id" in response.json()
    assert "amount" in response.json()
    assert "payment_date" in response.json()

def test_create_payment(db_session, seed_database, admin_headers):
    """Test creating a new payment."""
    payment_data = {
        "invoice_id": 1,
        "client_id": seed_database["test_client_1"].id,
        "project_id": 1,
        "amount": 5000.0,
        "payment_date": datetime.now().isoformat(),
        "method": "credit_card",
        "transaction_id": "txn_123456",
        "notes": "Test payment"
    }
    client = TestClient(app)
    response = client.post("/api/v1/payments/", json=payment_data, headers=admin_headers)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["invoice_id"] == payment_data["invoice_id"]
    assert response.json()["amount"] == payment_data["amount"]
    assert response.json()["method"] == payment_data["method"]

def test_update_payment(db_session, seed_database, admin_headers):
    """Test updating a payment."""
    update_data = {
        "notes": "Updated payment notes",
        "method": "bank_transfer"
    }
    client = TestClient(app)
    response = client.put("/api/v1/payments/1", json=update_data, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["notes"] == update_data["notes"]
    assert response.json()["method"] == update_data["method"]

def test_delete_payment(db_session, seed_database, admin_headers):
    """Test deleting a payment."""
    client = TestClient(app)
    response = client.delete("/api/v1/payments/1", headers=admin_headers)
    assert response.status_code == 204

def test_get_client_payments(db_session, seed_database, admin_headers):
    """Test getting all payments for a specific client."""
    client = TestClient(app)
    response = client.get(f"/api/v1/payments/client/{seed_database['test_client_1'].id}", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_invoice_payments(db_session, seed_database, admin_headers):
    """Test getting all payments for a specific invoice."""
    client = TestClient(app)
    response = client.get("/api/v1/payments/invoice/1", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for payment in response.json():
        assert payment["invoice_id"] == 1

def test_payment_stats(db_session, seed_database, admin_headers):
    """Test getting payment statistics."""
    client = TestClient(app)
    response = client.get("/api/v1/payments/stats", headers=admin_headers)
    assert response.status_code == 200
    assert "total_payments" in response.json()
    assert "total_amount" in response.json()

def test_financial_endpoint_errors(db_session, seed_database, admin_headers):
    """Test error cases for financial endpoints."""
    client = TestClient(app)
    # Test invalid invoice ID
    response = client.get("/api/v1/invoices/9999", headers=admin_headers)
    assert response.status_code == 404

    # Test invalid client ID when creating invoice
    invoice_data = {
        "client_id": 9999,
        "amount": 5000.0,
        "issue_date": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "status": "sent"
    }
    response = client.post("/api/v1/invoices/", json=invoice_data, headers=admin_headers)
    assert response.status_code in [404, 422]  # Allow both error codes
    
    # Test invalid payment method
    payment_data = {
        "invoice_id": 1,
        "client_id": seed_database["test_client_1"].id,
        "project_id": 1,
        "amount": 5000.0,
        "payment_date": datetime.now().isoformat(),
        "method": "invalid_method"
    }
    response = client.post("/api/v1/payments/", json=payment_data, headers=admin_headers)
    assert response.status_code == 422
