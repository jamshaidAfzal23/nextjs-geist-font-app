"""
Pydantic schemas for Dashboard data.
"""

from pydantic import BaseModel, Field

class DashboardStats(BaseModel):
    """
    Schema for the main dashboard statistics.
    """
    totalClients: int = Field(..., example=100)
    totalProjects: int = Field(..., example=50)
    totalRevenue: float = Field(..., example=150000.00)
    totalExpenses: float = Field(..., example=75000.00)
    activeProjects: int = Field(..., example=30)
    overdueProjects: int = Field(..., example=5)
    pendingPayments: float = Field(..., example=10000.00)
    monthlyGrowth: float = Field(..., example=5.2)

    class Config:
        orm_mode = True
