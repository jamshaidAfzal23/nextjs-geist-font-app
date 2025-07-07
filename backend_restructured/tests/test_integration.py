"""Integration tests for the Smart CRM SaaS backend."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from main import app

@pytest.mark.asyncio
async def test_client_project_workflow():
    """Test the complete client and project workflow."""
    # 1. Create a new client
    client_data = {
        "company_name": "Integration Test Company",
        "contact_person_name": "Test Contact",
        "email": "integration@test.com",
        "phone_number": "555-123-4567",
        "address": "123 Test St, Test City",
        "industry": "Technology",
        "platform_preference": "web",
        "category": "enterprise",
        "notes": "Integration test client",
        "assigned_user_id": 1
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create client
        client_response = await ac.post("/api/v1/clients", json=client_data)
        assert client_response.status_code == 201
        client_id = client_response.json()["id"]
        
        # 2. Create a project for the client
        project_data = {
            "name": "Integration Test Project",
            "description": "A test project for integration testing",
            "client_id": client_id,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "active",
            "budget": 10000.0,
            "assigned_user_id": 1
        }
        
        project_response = await ac.post("/api/v1/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # 3. Add a milestone to the project
        milestone_data = {
            "title": "Integration Test Milestone",
            "description": "A test milestone",
            "due_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "status": "pending"
        }
        
        milestone_response = await ac.post(f"/api/v1/projects/{project_id}/milestones", json=milestone_data)
        assert milestone_response.status_code == 201
        
        # 4. Create an invoice for the project
        invoice_data = {
            "client_id": client_id,
            "project_id": project_id,
            "amount": 5000.0,
            "issue_date": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "pending",
            "description": "Integration test invoice",
            "items": [
                {"description": "Service 1", "quantity": 1, "unit_price": 3000.0},
                {"description": "Service 2", "quantity": 2, "unit_price": 1000.0}
            ]
        }
        
        invoice_response = await ac.post("/api/v1/invoices", json=invoice_data)
        assert invoice_response.status_code == 201
        invoice_id = invoice_response.json()["id"]
        
        # 5. Record a payment for the invoice
        payment_data = {
            "invoice_id": invoice_id,
            "amount": 5000.0,
            "payment_date": datetime.now().isoformat(),
            "payment_method": "credit_card",
            "transaction_id": "txn_integration_test",
            "notes": "Integration test payment"
        }
        
        payment_response = await ac.post("/api/v1/payments", json=payment_data)
        assert payment_response.status_code == 201
        
        # 6. Update invoice status to paid
        invoice_update = {
            "status": "paid",
            "payment_date": datetime.now().isoformat()
        }
        
        invoice_update_response = await ac.put(f"/api/v1/invoices/{invoice_id}", json=invoice_update)
        assert invoice_update_response.status_code == 200
        assert invoice_update_response.json()["status"] == "paid"
        
        # 7. Add a note to the client
        note_data = {
            "content": "Integration test note for client"
        }
        
        note_response = await ac.post(f"/api/v1/clients/{client_id}/notes", json=note_data)
        assert note_response.status_code == 201
        
        # 8. Complete the project
        project_update = {
            "status": "completed",
            "end_date": datetime.now().isoformat()
        }
        
        project_update_response = await ac.put(f"/api/v1/projects/{project_id}", json=project_update)
        assert project_update_response.status_code == 200
        assert project_update_response.json()["status"] == "completed"
        
        # 9. Generate a client report
        client_report_response = await ac.get(f"/api/v1/reports/clients/{client_id}")
        assert client_report_response.status_code == 200
        assert client_report_response.json()["client_id"] == client_id
        
        # 10. Generate a project report
        project_report_response = await ac.get(f"/api/v1/reports/projects/{project_id}")
        assert project_report_response.status_code == 200
        assert project_report_response.json()["project_id"] == project_id
        
        # 11. Check client history
        history_response = await ac.get(f"/api/v1/clients/{client_id}/history")
        assert history_response.status_code == 200
        
        # 12. Clean up - delete the client (should cascade delete related entities)
        delete_response = await ac.delete(f"/api/v1/clients/{client_id}")
        assert delete_response.status_code == 204

@pytest.mark.asyncio
async def test_user_auth_workflow():
    """Test the user authentication workflow."""
    # 1. Register a new user
    user_data = {
        "email": "integration_auth@test.com",
        "password": "SecurePassword123!",
        "full_name": "Integration Auth User",
        "role": "user"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create user
        user_response = await ac.post("/api/v1/users", json=user_data)
        assert user_response.status_code == 201
        user_id = user_response.json()["id"]
        
        # 2. Login with the new user
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = await ac.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
        assert "token_type" in login_response.json()
        assert login_response.json()["token_type"] == "bearer"
        
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 3. Get current user info
        me_response = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == user_data["email"]
        
        # 4. Update user preferences
        pref_data = {
            "theme": "dark",
            "notifications_enabled": True,
            "dashboard_layout": "compact"
        }
        
        pref_response = await ac.put(f"/api/v1/users/{user_id}/preferences", json=pref_data, headers=headers)
        assert pref_response.status_code == 200
        assert pref_response.json()["theme"] == pref_data["theme"]
        
        # 5. Refresh token
        refresh_response = await ac.post("/api/v1/auth/refresh", headers=headers)
        assert refresh_response.status_code == 200
        assert "access_token" in refresh_response.json()
        
        # 6. Logout
        logout_response = await ac.post("/api/v1/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # 7. Verify token is invalidated
        invalid_token_response = await ac.get("/api/v1/auth/me", headers=headers)
        assert invalid_token_response.status_code == 401
        
        # 8. Clean up - delete the user
        # Login as admin first
        admin_login = {
            "username": "admin@example.com",
            "password": "admin_password"
        }
        
        admin_login_response = await ac.post("/api/v1/auth/login", data=admin_login)
        admin_token = admin_login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        delete_response = await ac.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
        assert delete_response.status_code == 204

@pytest.mark.asyncio
async def test_report_export_workflow():
    """Test the report generation and export workflow."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Get financial report for a date range
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_response = await ac.get(f"/api/v1/reports/financial?start_date={start_date}&end_date={end_date}")
        assert financial_response.status_code == 200
        
        # 2. Export financial report as Excel
        excel_response = await ac.get(f"/api/v1/reports/export/financial?start_date={start_date}&end_date={end_date}&format=excel")
        assert excel_response.status_code == 200
        assert excel_response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        
        # 3. Get team performance report
        team_response = await ac.get("/api/v1/reports/team/performance")
        assert team_response.status_code == 200
        
        # 4. Generate a custom report
        report_config = {
            "report_type": "custom",
            "title": "Integration Test Custom Report",
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "project_status": ["active", "completed"]
            },
            "metrics": ["revenue", "project_count"],
            "group_by": "month"
        }
        
        custom_response = await ac.post("/api/v1/reports/custom", json=report_config)
        assert custom_response.status_code == 200
        
        # 5. Export custom report as PDF
        custom_export_response = await ac.post("/api/v1/reports/export/custom?format=pdf", json=report_config)
        assert custom_export_response.status_code == 200
        assert custom_export_response.headers["content-type"] == "application/pdf"

@pytest.mark.asyncio
async def test_ai_analysis_workflow():
    """Test the AI analysis workflow."""
    # First create a client and project to analyze
    client_data = {
        "company_name": "AI Test Company",
        "contact_person_name": "AI Test Contact",
        "email": "ai@test.com",
        "phone_number": "555-987-6543",
        "address": "456 AI St, Test City",
        "industry": "Technology",
        "platform_preference": "web",
        "category": "enterprise",
        "notes": "AI test client",
        "assigned_user_id": 1
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create client
        client_response = await ac.post("/api/v1/clients", json=client_data)
        client_id = client_response.json()["id"]
        
        # Create project
        project_data = {
            "name": "AI Test Project",
            "description": "A test project for AI analysis",
            "client_id": client_id,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "status": "active",
            "budget": 15000.0,
            "assigned_user_id": 1
        }
        
        project_response = await ac.post("/api/v1/projects", json=project_data)
        project_id = project_response.json()["id"]
        
        # 1. Get client analysis
        client_analysis_response = await ac.get(f"/api/v1/ai/clients/{client_id}/analysis")
        assert client_analysis_response.status_code == 200
        assert client_analysis_response.json()["client_id"] == client_id
        
        # 2. Get project analysis
        project_analysis_response = await ac.get(f"/api/v1/ai/projects/{project_id}/analysis")
        assert project_analysis_response.status_code == 200
        assert project_analysis_response.json()["project_id"] == project_id
        
        # 3. Get client churn predictions
        churn_response = await ac.get("/api/v1/ai/clients/churn-prediction")
        assert churn_response.status_code == 200
        assert "predictions" in churn_response.json()
        
        # 4. Get client segmentation
        segment_response = await ac.get("/api/v1/ai/clients/segmentation")
        assert segment_response.status_code == 200
        assert "segments" in segment_response.json()
        
        # 5. Generate content for client communication
        generation_request = {
            "client_id": client_id,
            "communication_type": "follow_up",
            "context": "Project progress",
            "tone": "professional"
        }
        
        content_response = await ac.post("/api/v1/ai/generate/content", json=generation_request)
        assert content_response.status_code == 200
        assert "generated_content" in content_response.json()
        
        # 6. Analyze sentiment of a message
        sentiment_request = {
            "text": "We are very happy with the progress of the project and look forward to the next phase."
        }
        
        sentiment_response = await ac.post("/api/v1/ai/analyze/sentiment", json=sentiment_request)
        assert sentiment_response.status_code == 200
        assert sentiment_response.json()["sentiment"] == "positive"
        
        # 7. Get business insights
        insights_response = await ac.get("/api/v1/ai/insights/business")
        assert insights_response.status_code == 200
        assert "insights" in insights_response.json()
        
        # Clean up
        await ac.delete(f"/api/v1/clients/{client_id}")