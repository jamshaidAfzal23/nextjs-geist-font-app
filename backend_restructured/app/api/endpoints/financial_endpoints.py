"""Financial API endpoints for Smart CRM SaaS application.
This module defines all financial-related API routes including payments,
expenses, invoices, and financial analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from ...core.database import get_database_session
from ...core.rbac import require_permissions
from ...core.security import get_current_user
from ...models import Payment, Expense, Invoice, Project, Client, User
from ...models.financial_model import PaymentStatus, ExpenseCategory, InvoiceStatus
from ...schemas.financial_schemas import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentCreateBulk, PaymentUpdateBulk, PaymentDeleteBulk,
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseCreateBulk, ExpenseUpdateBulk, ExpenseDeleteBulk,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceCreateBulk, InvoiceUpdateBulk, InvoiceDeleteBulk,
    FinancialStats
)

# Create separate routers for each financial entity
payment_router = APIRouter(prefix="/payments", tags=["payments"])
expense_router = APIRouter(prefix="/expenses", tags=["expenses"])
invoice_router = APIRouter(prefix="/invoices", tags=["invoices"])
financial_router = APIRouter(prefix="/financial", tags=["financial-analytics"])

# Combine all financial routers
router = APIRouter()
router.include_router(payment_router)
router.include_router(expense_router)
router.include_router(invoice_router)
router.include_router(financial_router)

@financial_router.get("/stats", response_model=FinancialStats)
async def get_financial_stats(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_database_session)
):
    """Get comprehensive financial statistics."""
    # Set date filters
    if year and month:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, 1) + timedelta(days=32)
        end_date = end_date.replace(day=1) - timedelta(days=1)
    elif year:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
    else:
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31, 23, 59, 59)
    
    # Base queries
    payments_query = db.query(Payment).filter(
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    )
    expenses_query = db.query(Expense).filter(
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    )
    invoices_query = db.query(Invoice)

    # Apply additional filters
    if client_id:
        payments_query = payments_query.filter(Payment.client_id == client_id)
        expenses_query = expenses_query.filter(Expense.linked_project.has(client_id=client_id))
        invoices_query = invoices_query.filter(Invoice.client_id == client_id)
    
    if project_id:
        payments_query = payments_query.filter(Payment.project_id == project_id)
        expenses_query = expenses_query.filter(Expense.linked_project_id == project_id)

    # Calculate total revenue
    total_revenue = payments_query.filter(Payment.status == PaymentStatus.COMPLETED).with_entities(func.sum(Payment.amount)).scalar() or 0.0
    
    # Calculate total expenses
    total_expenses = expenses_query.with_entities(func.sum(Expense.amount)).scalar() or 0.0
    
    # Calculate net profit and margin
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Revenue by month
    revenue_by_month = {}
    monthly_revenue = payments_query.filter(
        Payment.status == PaymentStatus.COMPLETED
    ).group_by(extract('month', Payment.payment_date)).with_entities(extract('month', Payment.payment_date).label('month'), func.sum(Payment.amount).label('total')).all()
    
    for month_num, total in monthly_revenue:
        month_name = datetime(2000, int(month_num), 1).strftime('%B')
        revenue_by_month[month_name] = float(total)
    
    # Expenses by category
    expenses_by_category = {}
    category_expenses = expenses_query.group_by(Expense.category).with_entities(Expense.category, func.sum(Expense.amount).label('total')).all()
    
    for category, total in category_expenses:
        expenses_by_category[category] = float(total)
    
    # Outstanding invoices
    outstanding_invoices = invoices_query.filter(Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.OVERDUE])).with_entities(func.sum(Invoice.amount)).scalar() or 0.0
    
    # Average payment time (simplified calculation)
    avg_payment_time = None  # This would require more complex calculation
    
    return {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "profit_margin": profit_margin,
        "revenue_by_month": revenue_by_month,
        "expenses_by_category": expenses_by_category,
        "outstanding_invoices": outstanding_invoices,
        "average_payment_time": avg_payment_time
    }
