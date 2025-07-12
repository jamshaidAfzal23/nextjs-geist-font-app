"""
API endpoints for dashboard data.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_database_session
from ...models import Client, Project, Payment, Expense
from ...schemas.dashboard_schemas import DashboardStats
from sqlalchemy import func
from ...models.project_model import ProjectStatus

router = APIRouter(tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_database_session)):
    """
    Get statistics for the main dashboard.
    """
    total_clients = db.query(func.count(Client.id)).scalar()
    total_projects = db.query(func.count(Project.id)).scalar()
    total_revenue = db.query(func.sum(Payment.amount)).scalar() or 0.0
    total_expenses = db.query(func.sum(Expense.amount)).scalar() or 0.0
    active_projects = db.query(func.count(Project.id)).filter(Project.status == ProjectStatus.IN_PROGRESS).scalar()
    overdue_projects = db.query(func.count(Project.id)).filter(Project.status == ProjectStatus.COMPLETED, Project.end_date < func.now()).scalar()
    pending_payments = db.query(func.sum(Payment.amount)).filter(Payment.status == 'pending').scalar() or 0.0
    
    # Mock monthly growth for now
    monthly_growth = 12.5

    return {
        "totalClients": total_clients,
        "totalProjects": total_projects,
        "totalRevenue": total_revenue,
        "totalExpenses": total_expenses,
        "activeProjects": active_projects,
        "overdueProjects": overdue_projects,
        "pendingPayments": pending_payments,
        "monthlyGrowth": monthly_growth,
    }
