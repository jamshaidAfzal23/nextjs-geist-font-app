"""
API router for the Smart CRM SaaS application.
This module combines all the API endpoint routers into a single APIRouter.
"""

from fastapi import APIRouter

from .endpoints import (
    auth_endpoints,
    ai_endpoints,
    api_key_endpoints,
    automated_task_endpoints,
    backup_endpoints,
    client_endpoints,
    client_history_endpoints,
    client_note_endpoints,
    dashboard_endpoints,
    financial_endpoints,
    notification_endpoints,
    project_endpoints,
    project_milestone_endpoints,
    report_endpoints,
    report_template_endpoints,
    scheduled_report_endpoints,
    user_endpoints,
    user_preference_endpoints,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_endpoints.router, prefix="/auth", tags=["auth"])
api_router.include_router(ai_endpoints.router, prefix="/ai", tags=["ai"])
api_router.include_router(api_key_endpoints.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(automated_task_endpoints.router, prefix="/automated-tasks", tags=["automated-tasks"])
api_router.include_router(backup_endpoints.router, prefix="/backup", tags=["backup"])
api_router.include_router(user_endpoints.router, prefix="/users", tags=["users"])
api_router.include_router(user_preference_endpoints.router, prefix="/user-preferences", tags=["user-preferences"])
api_router.include_router(client_endpoints.router, prefix="/clients", tags=["clients"])
api_router.include_router(client_history_endpoints.router, prefix="/client-history", tags=["client-history"])
api_router.include_router(client_note_endpoints.router, prefix="/client-notes", tags=["client-notes"])
api_router.include_router(project_endpoints.router, prefix="/projects", tags=["projects"])
api_router.include_router(project_milestone_endpoints.router, prefix="/project-milestones", tags=["project-milestones"])
api_router.include_router(financial_endpoints.router, prefix="/financials", tags=["financials"])
api_router.include_router(dashboard_endpoints.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(notification_endpoints.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(report_endpoints.router, prefix="/reports", tags=["reports"])
api_router.include_router(report_template_endpoints.router, prefix="/report-templates", tags=["report-templates"])
api_router.include_router(scheduled_report_endpoints.router, prefix="/scheduled-reports", tags=["scheduled-reports"])