"""Comprehensive tests for client endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.schemas.client_schemas import ClientCreateBulk, ClientUpdateBulk, ClientDeleteBulk
from main import app

def test_get_clients(test_client, seed_database):
    """Test getting all clients."""
    response = test_client.get("/api/v1/clients/")
    assert response.status_code == 200
    assert "clients" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["clients"], list)
    assert response.json()["total"] >= 2  # We have 2 test clients

def test_get_client_by_id(test_client, seed_database):
    """Test getting a specific client by ID."""
    response = test_client.get("/api/v1/clients/1")
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["id"] == 1
    assert response.json()["company_name"] == "Test Company 1"

def test_create_client(test_client, seed_database, admin_headers):
    """Test creating a new client."""
    client_data = {
        "company_name": "New Test Company",
        "contact_person_name": "New Test Contact",
        "email": "newtest@example.com",
        "phone_number": "1234567890",
        "address": "123 Test St",
        "industry": "Technology",
        "platform_preference": "Web",
        "notes": "Test notes",
        "assigned_user_id": seed_database["admin_user"].id
    }
    response = test_client.post("/api/v1/clients/", json=client_data, headers=admin_headers)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["company_name"] == client_data["company_name"]
    assert response.json()["email"] == client_data["email"]

def test_update_client(test_client, seed_database, admin_headers):
    """Test updating a client."""
    update_data = {
        "company_name": "Updated Company",
        "contact_person_name": "Updated Contact",
        "industry": "Updated Industry"
    }
    response = test_client.put("/api/v1/clients/1", json=update_data, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["company_name"] == update_data["company_name"]
    assert response.json()["contact_person_name"] == update_data["contact_person_name"]
    assert response.json()["industry"] == update_data["industry"]

def test_delete_client(test_client, seed_database, admin_headers):
    """Test deleting a client."""
    response = test_client.delete("/api/v1/clients/2", headers=admin_headers)
    assert response.status_code == 204

def test_client_stats(test_client, seed_database):
    """Test getting client statistics."""
    response = test_client.get("/api/v1/clients/summary/stats")
    assert response.status_code == 200
    assert "total_clients" in response.json()
    assert "active_clients" in response.json()
    assert "clients_by_industry" in response.json()
    assert "clients_by_user" in response.json()
    assert "average_project_value" in response.json()
    assert "top_clients_by_value" in response.json()
    assert response.json()["total_clients"] >= 2

def test_client_search(test_client, seed_database):
    """Test client search functionality."""
    response = test_client.get("/api/v1/clients/search/advanced?search_term=Test Company")
    assert response.status_code == 200
    assert "clients" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["clients"], list)
    assert response.json()["total"] >= 1
    
def test_client_search_with_filters(test_client, seed_database):
    """Test client search with multiple filters."""
    response = test_client.get(
        "/api/v1/clients/search/advanced?search_term=Test&industry=Technology"
    )
    assert response.status_code == 200
    assert "clients" in response.json()
    assert "total" in response.json()

def test_client_endpoint_errors(test_client, seed_database, admin_headers):
    """Test error cases for client endpoints."""
    # Test invalid client ID
    response = test_client.get("/api/v1/clients/9999")
    assert response.status_code == 404

    # Test invalid update data (need auth headers for this test)
    response = test_client.put("/api/v1/clients/1", json={"email": "invalid-email"}, headers=admin_headers)
    assert response.status_code == 422

    # Test unauthorized access
    response = test_client.delete("/api/v1/clients/1")
    assert response.status_code in [401, 403]
        
def test_create_client_duplicate_email(test_client, seed_database, admin_headers):
    """Test creating a client with duplicate email."""
    # Try to create a client with existing email
    client_data = {
        "company_name": "Duplicate Company",
        "contact_person_name": "Duplicate Contact",
        "email": "john@testcompany1.com",  # This email already exists in seed data
        "assigned_user_id": seed_database["admin_user"].id
    }
    
    response = test_client.post("/api/v1/clients/", json=client_data, headers=admin_headers)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_bulk_operations(test_client, seed_database, admin_headers):
    """Test bulk client operations."""
    # Test bulk create
    bulk_create_data = {
        "clients": [
            {
                "company_name": "Bulk Company 1",
                "contact_person_name": "Bulk Contact 1",
                "email": "bulk1@example.com",
                "assigned_user_id": seed_database["admin_user"].id
            },
            {
                "company_name": "Bulk Company 2",
                "contact_person_name": "Bulk Contact 2",
                "email": "bulk2@example.com",
                "assigned_user_id": seed_database["admin_user"].id
            }
        ]
    }
    
    response = test_client.post("/api/v1/clients/bulk", json=bulk_create_data, headers=admin_headers)
    
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
    
    response = test_client.put("/api/v1/clients/bulk", json=bulk_update_data, headers=admin_headers)
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Test bulk delete - use different IDs to avoid conflicts
    bulk_delete_data = {
        "client_ids": [1, 2]
    }
    
    response = test_client.request("DELETE", "/api/v1/clients/bulk", json=bulk_delete_data, headers=admin_headers)
    
    assert response.status_code == 204
