"""Comprehensive tests for client history endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from datetime import datetime

from main import app
from app.models.client_history_model import ClientHistory

@pytest.mark.asyncio
async def test_get_client_history():
    """Test getting client history."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/1/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_client_history_pagination():
    """Test client history pagination."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/1/history?skip=0&limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 5

@pytest.mark.asyncio
async def test_get_client_history_not_found():
    """Test getting history for non-existent client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/9999/history")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_client_history_unauthorized():
    """Test unauthorized access to client history."""
    # Test without authentication
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/1/history")
    assert response.status_code in [401, 403]

    # Test with invalid token
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/clients/1/history",
            headers={"Authorization": "Bearer invalid_token"}
        )
    assert response.status_code in [401, 403]