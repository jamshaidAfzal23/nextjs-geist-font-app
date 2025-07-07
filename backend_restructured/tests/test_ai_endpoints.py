"""Comprehensive tests for AI analysis endpoints."""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import Session

from main import app

@pytest.mark.asyncio
async def test_client_analysis():
    """Test AI analysis of a client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/ai/clients/1/analysis")
    assert response.status_code == 200
    assert "client_id" in response.json()
    assert "analysis" in response.json()
    assert "recommendations" in response.json()
    assert "sentiment_score" in response.json()

@pytest.mark.asyncio
async def test_project_analysis():
    """Test AI analysis of a project."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/ai/projects/1/analysis")
    assert response.status_code == 200
    assert "project_id" in response.json()
    assert "analysis" in response.json()
    assert "risk_assessment" in response.json()
    assert "completion_prediction" in response.json()

@pytest.mark.asyncio
async def test_financial_forecast():
    """Test AI financial forecasting."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/ai/financial/forecast")
    assert response.status_code == 200
    assert "forecast_period" in response.json()
    assert "revenue_forecast" in response.json()
    assert "expense_forecast" in response.json()
    assert "profit_forecast" in response.json()

@pytest.mark.asyncio
async def test_client_churn_prediction():
    """Test AI client churn prediction."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/ai/clients/churn-prediction")
    assert response.status_code == 200
    assert "predictions" in response.json()
    assert isinstance(response.json()["predictions"], list)
    if response.json()["predictions"]:
        assert "client_id" in response.json()["predictions"][0]
        assert "churn_probability" in response.json()["predictions"][0]
        assert "risk_factors" in response.json()["predictions"][0]

@pytest.mark.asyncio
async def test_client_segmentation():
    """Test AI client segmentation."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/ai/clients/segmentation")
    assert response.status_code == 200
    assert "segments" in response.json()
    assert isinstance(response.json()["segments"], list)
    if response.json()["segments"]:
        assert "segment_name" in response.json()["segments"][0]
        assert "client_ids" in response.json()["segments"][0]
        assert "characteristics" in response.json()["segments"][0]

@pytest.mark.asyncio
async def test_content_generation():
    """Test AI content generation for client communication."""
    generation_request = {
        "client_id": 1,
        "communication_type": "follow_up",
        "context": "Project completion",
        "tone": "professional"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/ai/generate/content", json=generation_request)
    assert response.status_code == 200
    assert "generated_content" in response.json()
    assert "subject" in response.json()
    assert "body" in response.json()

@pytest.mark.asyncio
async def test_sentiment_analysis():
    """Test AI sentiment analysis of client communication."""
    analysis_request = {
        "text": "We are very satisfied with the project outcome and looking forward to working with you again."
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/ai/analyze/sentiment", json=analysis_request)
    assert response.status_code == 200
    assert "sentiment" in response.json()
    assert "score" in response.json()
    assert "entities" in response.json()

@pytest.mark.asyncio
async def test_business_insights():
    """Test AI business insights generation."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/ai/insights/business")
    assert response.status_code == 200
    assert "insights" in response.json()
    assert isinstance(response.json()["insights"], list)
    assert "trends" in response.json()
    assert "opportunities" in response.json()

@pytest.mark.asyncio
async def test_ai_endpoint_errors():
    """Test error cases for AI endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test invalid client ID
        response = await ac.get("/api/v1/ai/clients/9999/analysis")
        assert response.status_code == 404

        # Test invalid project ID
        response = await ac.get("/api/v1/ai/projects/9999/analysis")
        assert response.status_code == 404
        
        # Test invalid content generation request
        invalid_request = {
            "client_id": 1,
            "communication_type": "invalid_type"
        }
        response = await ac.post("/api/v1/ai/generate/content", json=invalid_request)
        assert response.status_code == 422
        
        # Test empty text for sentiment analysis
        empty_text = {"text": ""}
        response = await ac.post("/api/v1/ai/analyze/sentiment", json=empty_text)
        assert response.status_code == 400