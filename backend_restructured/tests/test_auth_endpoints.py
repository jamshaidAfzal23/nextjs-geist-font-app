"""Comprehensive tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from main import app

@pytest.mark.asyncio
async def test_login(db_session):
    """Test user login."""
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(db_session):
    """Test login with invalid credentials."""
    login_data = {
        "username": "wrong@example.com",
        "password": "wrongpassword"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_get_current_user(db_session):
    """Test getting current user information."""
    # First login to get token
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_response = await ac.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use token to get current user
        response = await ac.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert "id" in response.json()
    assert "email" in response.json()
    assert "role" in response.json()

@pytest.mark.asyncio
async def test_refresh_token(db_session):
    """Test refreshing access token."""
    # First login to get token
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_response = await ac.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use token to refresh
        response = await ac.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

@pytest.mark.asyncio
async def test_logout(db_session):
    """Test user logout."""
    # First login to get token
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_response = await ac.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Use token to logout
        response = await ac.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Note: In a stateless JWT implementation, tokens remain valid until expiration
    # The logout endpoint exists for API completeness but doesn't invalidate tokens server-side
    # In a real application, you might implement token blacklisting or use shorter expiration times

@pytest.mark.asyncio
async def test_unauthorized_access(db_session):
    """Test accessing protected endpoints without authentication."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Try to access protected endpoint without token
        response = await ac.get("/api/v1/users/me")
    assert response.status_code in [401, 403]
    
    # Try with invalid token
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
    assert response.status_code in [401, 403]
