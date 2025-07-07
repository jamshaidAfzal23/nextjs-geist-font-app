"""Comprehensive tests for financial endpoints (invoices and payments)."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from main import app

# Invoice Tests
@pytest.mark.asyncio
async def test_get_invoices():
    """Test getting all invoices."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/invoices")
    assert response.status_code == 200
    assert "invoices" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["invoices"], list)

@pytest.mark.asyncio
async def test_get_invoice_by_id():
    """Test getting a specific invoice by ID."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/invoices/1")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "client_id" in response.json()
    assert "amount" in response.json()
    assert "status" in response.json()

@pytest.mark.asyncio
async def test_create_invoice():
    """Test creating a new invoice."""
    invoice_data = {
        "client_id": 1,
        "project_id": 1,
        "amount": 5000.0,
        "issue_date": datetime.now().isoformat(),
        "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "status": "pending",
        "description": "Test invoice",
        "items": [
            {"description": "Service 1", "quantity": 1, "unit_price": 3000.0},
            {"description": "Service 2", "quantity": 2, "unit_price": 1000.0}
        ]
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/invoices", json=invoice_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["client_id"] == invoice_data["client_id"]
    assert response.json()["amount"] == invoice_data["amount"]
    assert response.json()["status"] == invoice_data["status"]
    assert "items" in response.json()
    assert len(response.json()["items"]) == 2

@pytest.mark.asyncio
async def test_update_invoice():
    """Test updating an invoice."""
    update_data = {
        "status": "paid",
        "payment_date": datetime.now().isoformat()
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/api/v1/invoices/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == update_data["status"]
    assert "payment_date" in response.json()

@pytest.mark.asyncio
async def test_delete_invoice():
    """Test deleting an invoice."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/invoices/1")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_get_client_invoices():
    """Test getting all invoices for a specific client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/invoices/client/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for invoice in response.json():
        assert invoice["client_id"] == 1

@pytest.mark.asyncio
async def test_invoice_stats():
    """Test getting invoice statistics."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/invoices/stats")
    assert response.status_code == 200
    assert "total_invoices" in response.json()
    assert "pending_invoices" in response.json()
    assert "paid_invoices" in response.json()
    assert "total_amount" in response.json()
    assert "pending_amount" in response.json()

# Payment Tests
@pytest.mark.asyncio
async def test_get_payments():
    """Test getting all payments."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/payments")
    assert response.status_code == 200
    assert "payments" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["payments"], list)

@pytest.mark.asyncio
async def test_get_payment_by_id():
    """Test getting a specific payment by ID."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/payments/1")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "invoice_id" in response.json()
    assert "amount" in response.json()
    assert "payment_date" in response.json()

@pytest.mark.asyncio
async def test_create_payment():
    """Test creating a new payment."""
    payment_data = {
        "invoice_id": 1,
        "amount": 5000.0,
        "payment_date": datetime.now().isoformat(),
        "payment_method": "credit_card",
        "transaction_id": "txn_123456",
        "notes": "Test payment"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/payments", json=payment_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["invoice_id"] == payment_data["invoice_id"]
    assert response.json()["amount"] == payment_data["amount"]
    assert response.json()["payment_method"] == payment_data["payment_method"]

@pytest.mark.asyncio
async def test_update_payment():
    """Test updating a payment."""
    update_data = {
        "notes": "Updated payment notes",
        "payment_method": "bank_transfer"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/api/v1/payments/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["notes"] == update_data["notes"]
    assert response.json()["payment_method"] == update_data["payment_method"]

@pytest.mark.asyncio
async def test_delete_payment():
    """Test deleting a payment."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/payments/1")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_get_client_payments():
    """Test getting all payments for a specific client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/payments/client/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_invoice_payments():
    """Test getting all payments for a specific invoice."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/payments/invoice/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for payment in response.json():
        assert payment["invoice_id"] == 1

@pytest.mark.asyncio
async def test_payment_stats():
    """Test getting payment statistics."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/payments/stats")
    assert response.status_code == 200
    assert "total_payments" in response.json()
    assert "total_amount" in response.json()
    assert "payment_methods" in response.json()

@pytest.mark.asyncio
async def test_financial_endpoint_errors():
    """Test error cases for financial endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test invalid invoice ID
        response = await ac.get("/api/v1/invoices/9999")
        assert response.status_code == 404

        # Test invalid client ID when creating invoice
        invoice_data = {
            "client_id": 9999,
            "amount": 5000.0,
            "issue_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "pending"
        }
        response = await ac.post("/api/v1/invoices", json=invoice_data)
        assert response.status_code == 404
        
        # Test invalid payment method
        payment_data = {
            "invoice_id": 1,
            "amount": 5000.0,
            "payment_date": datetime.now().isoformat(),
            "payment_method": "invalid_method"
        }
        response = await ac.post("/api/v1/payments", json=payment_data)
        assert response.status_code == 422