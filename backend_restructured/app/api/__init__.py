"""
API package for Smart CRM SaaS application.
This module initializes and configures all API routes.
"""

from fastapi import APIRouter
from .endpoints.user_endpoints import router as user_router
from .endpoints.client_endpoints import router as client_router
from .endpoints.project_endpoints import router as project_router
from .endpoints.financial_endpoints import financial_main_router
from .endpoints.dashboard_endpoints import router as dashboard_router

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(user_router, prefix="/api/v1")
api_router.include_router(client_router, prefix="/api/v1")
api_router.include_router(project_router, prefix="/api/v1")
api_router.include_router(financial_main_router, prefix="/api/v1")
api_router.include_router(dashboard_router, prefix="/api/v1")

# Export router for use in main application
__all__ = ["api_router"]
