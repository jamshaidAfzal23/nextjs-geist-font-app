"""Comprehensive tests for report endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from main import app

@pytest.mark.asyncio
async def test_get_client_report():
    """Test getting a client report."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/clients/1")
    assert response.status_code == 200
    assert "client_id" in response.json()
    assert "client_name" in response.json()
    assert "projects" in response.json()
    assert "invoices" in response.json()
    assert "payments" in response.json()
    assert "total_value" in response.json()

@pytest.mark.asyncio
async def test_get_project_report():
    """Test getting a project report."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/projects/1")
    assert response.status_code == 200
    assert "project_id" in response.json()
    assert "project_name" in response.json()
    assert "client" in response.json()
    assert "milestones" in response.json()
    assert "invoices" in response.json()
    assert "budget" in response.json()
    assert "expenses" in response.json()

@pytest.mark.asyncio
async def test_get_financial_report():
    """Test getting a financial report."""
    # Test with date range
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/reports/financial?start_date={start_date}&end_date={end_date}")
    assert response.status_code == 200
    assert "period" in response.json()
    assert "revenue" in response.json()
    assert "expenses" in response.json()
    assert "profit" in response.json()
    assert "invoices" in response.json()
    assert "payments" in response.json()

@pytest.mark.asyncio
async def test_get_user_performance_report():
    """Test getting a user performance report."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/users/1/performance")
    assert response.status_code == 200
    assert "user_id" in response.json()
    assert "user_name" in response.json()
    assert "projects_managed" in response.json()
    assert "clients_managed" in response.json()
    assert "revenue_generated" in response.json()
    assert "project_completion_rate" in response.json()

@pytest.mark.asyncio
async def test_get_team_performance_report():
    """Test getting a team performance report."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/team/performance")
    assert response.status_code == 200
    assert "period" in response.json()
    assert "team_size" in response.json()
    assert "total_projects" in response.json()
    assert "completed_projects" in response.json()
    assert "total_clients" in response.json()
    assert "total_revenue" in response.json()
    assert "user_performance" in response.json()
    assert isinstance(response.json()["user_performance"], list)

@pytest.mark.asyncio
async def test_export_client_report():
    """Test exporting a client report."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/export/clients/1?format=pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/export/clients/1?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"

@pytest.mark.asyncio
async def test_export_financial_report():
    """Test exporting a financial report."""
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/reports/export/financial?start_date={start_date}&end_date={end_date}&format=excel")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

@pytest.mark.asyncio
async def test_get_dashboard_summary():
    """Test getting a dashboard summary report."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/reports/dashboard/summary")
    assert response.status_code == 200
    assert "active_projects" in response.json()
    assert "pending_invoices" in response.json()
    assert "recent_payments" in response.json()
    assert "client_acquisition" in response.json()
    assert "revenue_trend" in response.json()

@pytest.mark.asyncio
async def test_custom_report_generation():
    """Test generating a custom report."""
    report_config = {
        "report_type": "custom",
        "title": "Custom Client Revenue Report",
        "filters": {
            "start_date": (datetime.now() - timedelta(days=90)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "client_ids": [1, 2, 3],
            "project_status": ["active", "completed"],
            "min_value": 1000
        },
        "metrics": ["revenue", "project_count", "average_project_value"],
        "group_by": "client"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/reports/custom", json=report_config)
    assert response.status_code == 200
    assert "title" in response.json()
    assert "generated_at" in response.json()
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)

@pytest.mark.asyncio
async def test_report_endpoint_errors():
    """Test error cases for report endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test invalid client ID
        response = await ac.get("/api/v1/reports/clients/9999")
        assert response.status_code == 404

        # Test invalid project ID
        response = await ac.get("/api/v1/reports/projects/9999")
        assert response.status_code == 404
        
        # Test invalid date format
        response = await ac.get("/api/v1/reports/financial?start_date=invalid-date&end_date=2023-12-31")
        assert response.status_code == 422
        
        # Test invalid export format
        response = await ac.get("/api/v1/reports/export/clients/1?format=invalid")
        assert response.status_code == 400
        
        # Test invalid custom report configuration
        invalid_config = {
            "report_type": "invalid_type",
            "title": "Invalid Report"
        }
        response = await ac.post("/api/v1/reports/custom", json=invalid_config)
        assert response.status_code == 422