"""
Models package for Smart CRM SaaS application.
This module imports and exposes all database models for easy access.
"""

from .user_model import User
from .client_model import Client
from .project_model import Project, ProjectStatus, ProjectPriority
from .financial_model import Payment, Expense, Invoice, PaymentStatus, PaymentMethod, ExpenseCategory, InvoiceStatus

# Export all models for easy importing
__all__ = [
    "User",
    "Client", 
    "Project",
    "Payment",
    "Expense",
    "Invoice",
    "ProjectStatus",
    "ProjectPriority",
    "PaymentStatus",
    "PaymentMethod",
    "ExpenseCategory",
    "InvoiceStatus"
]
