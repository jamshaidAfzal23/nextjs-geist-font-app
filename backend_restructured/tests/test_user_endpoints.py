"""Comprehensive tests for user endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from main import app
from app.core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def admin_token():
    """Create an admin token for testing."""
    access_token = create_access_token(
        data={"sub": "admin@example.com", "role": "admin"},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def user_token():
    """Create a user token for testing."""
    access_token = create_access_token(
        data={"sub": "user@example.com", "role": "user"},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

def test_get_users(admin_token):
    """Test getting all users."""
    response = client.get("/api/v1/users", headers=admin_token)       
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "size" in response.json()
    assert "pages" in response.json()
    assert isinstance(response.json()["items"], list)

def test_get_user_by_id(admin_token):
    """Test getting a specific user by ID."""
    response = client.get("/api/v1/users/1", headers=admin_token)
    assert response.status_code == 200
    assert "id" in response.json()
    assert "email" in response.json()
    assert "role" in response.json()

def test_create_user(admin_token):
    """Test creating a new user."""
    user_data = {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "full_name": "New User",
        "role": "user"
    }
    response = client.post("/api/v1/users", json=user_data, headers=admin_token)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == user_data["email"]
    assert response.json()["full_name"] == user_data["full_name"]
    assert response.json()["role"] == user_data["role"]
    assert "password" not in response.json()  # Password should not be returned

def test_update_user(admin_token):
    """Test updating a user."""
    update_data = {
        "full_name": "Updated Name",
        "role": "admin"
    }
    response = client.put("/api/v1/users/1", json=update_data, headers=admin_token)
    assert response.status_code == 200
    assert response.json()["full_name"] == update_data["full_name"]
    assert response.json()["role"] == update_data["role"]

def test_delete_user(admin_token):
    """Test deleting a user."""
    # First create a user to delete
    user_data = {
        "email": "todelete@example.com",
        "password": "securepassword123",
        "full_name": "To Delete",
        "role": "user"
    }
    create_response = client.post("/api/v1/users", json=user_data, headers=admin_token)
    user_id = create_response.json()["id"]
    
    # Then delete it
    delete_response = client.delete(f"/api/v1/users/{user_id}", headers=admin_token)
    assert delete_response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/users/{user_id}", headers=admin_token)
    assert get_response.status_code == 404

def test_user_search(admin_token):
    """Test user search functionality."""
    response = client.get("/api/v1/users?search=admin", headers=admin_token)
    assert response.status_code == 200
    assert "users" in response.json()
    assert "total" in response.json()

def test_user_preferences(user_token):
    """Test user preferences endpoints."""
    # Get user preferences
    response = client.get("/api/v1/users/me/preferences", headers=user_token)
    assert response.status_code == 200
    
    # Update user preferences
    pref_data = {
        "theme": "dark",
        "notifications_enabled": True,
        "dashboard_layout": "compact"
    }
    response = client.put("/api/v1/users/me/preferences", json=pref_data, headers=user_token)
    assert response.status_code == 200
    assert response.json()["theme"] == pref_data["theme"]
    assert response.json()["notifications_enabled"] == pref_data["notifications_enabled"]

def test_user_endpoint_errors(admin_token):
    """Test error cases for user endpoints."""
    # Test invalid user ID
    response = client.get("/api/v1/users/9999", headers=admin_token)
    assert response.status_code == 404

    # Test invalid update data
    response = client.put("/api/v1/users/1", json={"role": "invalid_role"}, headers=admin_token)
    assert response.status_code == 422

    # Test duplicate email
    user_data = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "full_name": "Duplicate User",
        "role": "user"
    }
    client.post("/api/v1/users", json=user_data, headers=admin_token)
    response = client.post("/api/v1/users", json=user_data, headers=admin_token)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]