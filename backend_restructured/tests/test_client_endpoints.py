"""Comprehensive tests for client endpoints."""
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.schemas.client_schemas import ClientCreateBulk, ClientUpdateBulk, ClientDeleteBulk
from main import app

@pytest.mark.asyncio
async def test_get_clients():
    """Test getting all clients."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients")
    assert response.status_code == 200
    assert "clients" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["clients"], list)

@pytest.mark.asyncio
async def test_get_client_by_id():
    """Test getting a specific client by ID."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/1")
    assert response.status_code == 200
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_create_client():
    """Test creating a new client."""
    client_data = {
        "company_name": "Test Company",
        "contact_person_name": "Test Contact",
        "email": "test@example.com",
        "phone_number": "1234567890",
        "address": "123 Test St",
        "industry": "Technology",
        "platform_preference": "Web",
        "notes": "Test notes",
        "assigned_user_id": 1
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/clients", json=client_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["company_name"] == client_data["company_name"]
    assert response.json()["email"] == client_data["email"]

@pytest.mark.asyncio
async def test_update_client():
    """Test updating a client."""
    update_data = {
        "company_name": "Updated Company",
        "contact_person_name": "Updated Contact",
        "industry": "Updated Industry"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/api/v1/clients/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["company_name"] == update_data["company_name"]
    assert response.json()["contact_person_name"] == update_data["contact_person_name"]
    assert response.json()["industry"] == update_data["industry"]

@pytest.mark.asyncio
async def test_delete_client():
    """Test deleting a client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/clients/1")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_client_stats():
    """Test getting client statistics."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/summary/stats")
    assert response.status_code == 200
    assert "total_clients" in response.json()
    assert "active_clients" in response.json()
    assert "clients_by_industry" in response.json()
    assert "clients_by_user" in response.json()
    assert "average_project_value" in response.json()
    assert "top_clients_by_value" in response.json()

@pytest.mark.asyncio
async def test_client_search():
    """Test client search functionality."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/search/advanced?search_term=test")
    assert response.status_code == 200
    assert "clients" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["clients"], list)
    
@pytest.mark.asyncio
async def test_client_search_with_filters():
    """Test client search with multiple filters."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/clients/search/advanced?search_term=test&industry=Technology&has_active_projects=true"
        )
    assert response.status_code == 200
    assert "clients" in response.json()
    assert "total" in response.json()

@pytest.mark.asyncio
async def test_client_endpoint_errors():
    """Test error cases for client endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test invalid client ID
        response = await ac.get("/api/v1/clients/9999")
        assert response.status_code == 404

        # Test invalid update data
        response = await ac.put("/api/v1/clients/1", json={"email": "invalid-email"})
        assert response.status_code == 422

        # Test unauthorized access
        response = await ac.delete("/api/v1/clients/1")
        assert response.status_code in [401, 403]
        
@pytest.mark.asyncio
async def test_create_client_duplicate_email():
    """Test creating a client with duplicate email."""
    # First create a client
    client_data = {
        "company_name": "Test Company",
        "contact_person_name": "Test Contact",
        "email": "duplicate@example.com",
        "assigned_user_id": 1
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create first client
        await ac.post("/api/v1/clients", json=client_data)
        
        # Try to create another with same email
        response = await ac.post("/api/v1/clients", json=client_data)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_bulk_operations():
    """Test bulk client operations."""
    # Test bulk create
    bulk_create_data = {
        "clients": [
            {
                "company_name": "Bulk Company 1",
                "contact_person_name": "Bulk Contact 1",
                "email": "bulk1@example.com",
                "assigned_user_id": 1
            },
            {
                "company_name": "Bulk Company 2",
                "contact_person_name": "Bulk Contact 2",
                "email": "bulk2@example.com",
                "assigned_user_id": 1
            }
        ]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/clients/bulk", json=bulk_create_data)
    
    assert response.status_code == 201
    assert len(response.json()) == 2
    
    # Test bulk update
    bulk_update_data = {
        "clients": [
            {
                "id": 1,
                "company_name": "Updated Bulk 1"
            },
            {
                "id": 2,
                "company_name": "Updated Bulk 2"
            }
        ]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/api/v1/clients/bulk", json=bulk_update_data)
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Test bulk delete
    bulk_delete_data = {
        "client_ids": [1, 2]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/clients/bulk", json=bulk_delete_data)
    
    assert response.status_code == 204