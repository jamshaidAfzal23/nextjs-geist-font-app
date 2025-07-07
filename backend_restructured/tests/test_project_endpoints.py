"""Comprehensive tests for project endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from main import app

@pytest.mark.asyncio
async def test_get_projects():
    """Test getting all projects."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects")
    assert response.status_code == 200
    assert "projects" in response.json()
    assert "total" in response.json()
    assert isinstance(response.json()["projects"], list)

@pytest.mark.asyncio
async def test_get_project_by_id():
    """Test getting a specific project by ID."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects/1")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "name" in response.json()
    assert "client_id" in response.json()

@pytest.mark.asyncio
async def test_create_project():
    """Test creating a new project."""
    project_data = {
        "name": "Test Project",
        "description": "A test project",
        "client_id": 1,
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "status": "active",
        "budget": 10000.0,
        "assigned_user_id": 1
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/projects", json=project_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == project_data["name"]
    assert response.json()["client_id"] == project_data["client_id"]

@pytest.mark.asyncio
async def test_update_project():
    """Test updating a project."""
    update_data = {
        "name": "Updated Project",
        "status": "completed",
        "budget": 15000.0
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/api/v1/projects/1", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["status"] == update_data["status"]
    assert response.json()["budget"] == update_data["budget"]

@pytest.mark.asyncio
async def test_delete_project():
    """Test deleting a project."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/projects/1")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_get_client_projects():
    """Test getting all projects for a specific client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects/client/1/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for project in response.json():
        assert project["client_id"] == 1

@pytest.mark.asyncio
async def test_project_stats():
    """Test getting project statistics."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects/stats")
    assert response.status_code == 200
    assert "total_projects" in response.json()
    assert "active_projects" in response.json()
    assert "completed_projects" in response.json()
    assert "total_budget" in response.json()

@pytest.mark.asyncio
async def test_project_milestones():
    """Test project milestone endpoints."""
    # Create a milestone
    milestone_data = {
        "title": "Test Milestone",
        "description": "A test milestone",
        "due_date": (datetime.now() + timedelta(days=15)).isoformat(),
        "status": "pending"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/projects/1/milestones", json=milestone_data)
    assert response.status_code == 201
    assert "id" in response.json()
    milestone_id = response.json()["id"]
    
    # Get milestones
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/projects/1/milestones")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Update milestone
    update_data = {"status": "completed"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/api/v1/projects/milestones/{milestone_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    
    # Delete milestone
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/projects/milestones/{milestone_id}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_project_endpoint_errors():
    """Test error cases for project endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test invalid project ID
        response = await ac.get("/api/v1/projects/9999")
        assert response.status_code == 404

        # Test invalid client ID when creating project
        project_data = {
            "name": "Invalid Client Project",
            "client_id": 9999,
            "start_date": datetime.now().isoformat(),
            "status": "active",
            "assigned_user_id": 1
        }
        response = await ac.post("/api/v1/projects", json=project_data)
        assert response.status_code == 404
        
        # Test invalid status value
        update_data = {"status": "invalid_status"}
        response = await ac.put("/api/v1/projects/1", json=update_data)
        assert response.status_code == 422