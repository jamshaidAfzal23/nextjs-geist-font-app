"""
Pydantic schemas for Dashboard data.
"""

from pydantic import BaseModel

class DashboardStats(BaseModel):
    """
    Schema for the main dashboard statistics.
    """
    totalClients: int
    totalProjects: int
    totalRevenue: float
    totalExpenses: float
    activeProjects: int
    overdueProjects: int
    pendingPayments: float
    monthlyGrowth: float

    class Config:
        orm_mode = True
