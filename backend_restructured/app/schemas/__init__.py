"""
Schemas package for Smart CRM SaaS application.
This module imports and exposes all Pydantic schemas for data validation and serialization.
"""

from .user_schemas import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserLogin, 
    UserToken, UserListResponse, PasswordChange
)
from .client_schemas import (
    ClientBase, ClientCreate, ClientUpdate, ClientResponse,
    ClientListResponse, ClientSummary, ClientSearchFilters, ClientStats
)
from .project_schemas import (
    ProjectBase, ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectListResponse, ProjectSummary, ProjectSearchFilters,
    ProjectStats, ProjectMilestone
)
from .financial_schemas import (
    # Payment schemas
    PaymentBase, PaymentCreate, PaymentUpdate, PaymentResponse,
    # Expense schemas
    ExpenseBase, ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    # Invoice schemas
    InvoiceBase, InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    # Financial statistics
    FinancialStats
)

# Export all schemas for easy importing
__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "UserLogin", "UserToken", "UserListResponse", "PasswordChange",
    
    # Client schemas
    "ClientBase", "ClientCreate", "ClientUpdate", "ClientResponse",
    "ClientListResponse", "ClientSummary", "ClientSearchFilters",
    "ClientStats",
    
    # Project schemas
    "ProjectBase", "ProjectCreate", "ProjectUpdate", "ProjectResponse",
    "ProjectListResponse", "ProjectSummary", "ProjectSearchFilters",
    "ProjectStats", "ProjectMilestone",
    
    # Financial schemas
    "PaymentBase", "PaymentCreate", "PaymentUpdate", "PaymentResponse",
    "ExpenseBase", "ExpenseCreate", "ExpenseUpdate", "ExpenseResponse",
    "InvoiceBase", "InvoiceCreate", "InvoiceUpdate", "InvoiceResponse",
    "FinancialStats"
]
