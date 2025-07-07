"""Comprehensive tests for client note endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from datetime import datetime

from main import app
from app.models.client_note_model import ClientNote

@pytest.mark.asyncio
async def test_get_client_notes():
    """Test getting client notes."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/1/notes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_create_client_note():
    """Test creating a client note."""
    note_data = {
        "content": "Test note content"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/clients/1/notes", json=note_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["content"] == note_data["content"]

@pytest.mark.asyncio
async def test_delete_client_note():
    """Test deleting a client note."""
    # First create a note
    note_data = {"content": "Note to be deleted"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_response = await ac.post("/api/v1/clients/1/notes", json=note_data)
        note_id = create_response.json()["id"]
        
        # Then delete it
        delete_response = await ac.delete(f"/api/v1/clients/notes/{note_id}")
    assert delete_response.status_code == 204
    
    # Verify it's deleted
    async with AsyncClient(app=app, base_url="http://test") as ac:
        get_response = await ac.get("/api/v1/clients/1/notes")
        notes = get_response.json()
    assert all(note["id"] != note_id for note in notes)

@pytest.mark.asyncio
async def test_get_client_notes_pagination():
    """Test client notes pagination."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/1/notes?skip=0&limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 5

@pytest.mark.asyncio
async def test_create_note_client_not_found():
    """Test creating a note for non-existent client."""
    note_data = {"content": "Test note content"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/clients/9999/notes", json=note_data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_note_not_found():
    """Test deleting a non-existent note."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/clients/notes/9999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_note_unauthorized():
    """Test unauthorized note deletion."""
    # Create a note as user 1
    note_data = {"content": "Note by user 1"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Authenticate as user 1
        create_response = await ac.post("/api/v1/clients/1/notes", json=note_data)
        note_id = create_response.json()["id"]
        
        # Try to delete as user 2
        # This would require proper authentication setup in the test
        delete_response = await ac.delete(
            f"/api/v1/clients/notes/{note_id}",
            headers={"Authorization": "Bearer user2_token"}
        )
    assert delete_response.status_code in [401, 403]

@pytest.mark.asyncio
async def test_client_notes_unauthorized():
    """Test unauthorized access to client notes."""
    # Test without authentication
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clients/1/notes")
    assert response.status_code in [401, 403]

    # Test with invalid token
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/clients/1/notes",
            headers={"Authorization": "Bearer invalid_token"}
        )
    assert response.status_code in [401, 403]