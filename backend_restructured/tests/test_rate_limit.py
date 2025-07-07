"""Test rate limiting functionality."""

import pytest
from httpx import AsyncClient
from slowapi.errors import RateLimitExceeded
from main import app

@pytest.mark.asyncio
async def test_rate_limit():
    """Test rate limiting on endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Make multiple requests to trigger rate limit
        for _ in range(5):
            response = await ac.get("/api/v1/users/me")
        
        # Next request should be rate limited
        response = await ac.get("/api/v1/users/me")
        assert response.status_code == 429  # Too Many Requests