"""
API endpoints package for Smart CRM SaaS application.
This package contains all the API endpoint modules.
"""

# Import all endpoint modules to make them available for the API router
from . import (
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

__all__ = [
    "auth_endpoints",
    "ai_endpoints", 
    "api_key_endpoints",
    "automated_task_endpoints",
    "backup_endpoints",
    "client_endpoints",
    "client_history_endpoints",
    "client_note_endpoints",
    "dashboard_endpoints",
    "financial_endpoints",
    "notification_endpoints",
    "project_endpoints",
    "project_milestone_endpoints",
    "report_endpoints",
    "report_template_endpoints",
    "scheduled_report_endpoints",
    "user_endpoints",
    "user_preference_endpoints",
]
