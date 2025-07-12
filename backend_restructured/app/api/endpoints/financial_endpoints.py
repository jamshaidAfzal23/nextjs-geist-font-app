"""Financial API endpoints for Smart CRM SaaS application.
This module defines all financial-related API routes including payments,
expenses, invoices, and financial analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json
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
payment_router = APIRouter(tags=["payments"])
expense_router = APIRouter(tags=["expenses"])
invoice_router = APIRouter(tags=["invoices"])
financial_router = APIRouter(tags=["financial-analytics"])

# Invoice endpoints
@invoice_router.get("/", response_model=Dict)
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get all invoices with pagination."""
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    total = db.query(Invoice).count()
    
    # Convert invoices to dict and parse JSON items
    invoice_list = []
    for invoice in invoices:
        invoice_dict = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "client_id": invoice.client_id,
            "amount": invoice.amount,
            "status": invoice.status,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "paid_date": invoice.paid_date,
            "items": json.loads(invoice.items) if invoice.items else [],
            "notes": invoice.notes,
            "created_at": invoice.created_at,
            "updated_at": invoice.updated_at
        }
        invoice_list.append(invoice_dict)
    
    return {"invoices": invoice_list, "total": total}

@invoice_router.get("/{invoice_id}", response_model=Dict)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific invoice by ID."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Convert to dict and parse JSON items
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "client_id": invoice.client_id,
        "amount": invoice.amount,
        "status": invoice.status,
        "issue_date": invoice.issue_date,
        "due_date": invoice.due_date,
        "paid_date": invoice.paid_date,
        "items": json.loads(invoice.items) if invoice.items else [],
        "notes": invoice.notes,
        "created_at": invoice.created_at,
        "updated_at": invoice.updated_at
    }

@invoice_router.post("/", response_model=Dict, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new invoice."""
    invoice_data = invoice.dict()
    # Convert items list to JSON string
    if 'items' in invoice_data:
        invoice_data['items'] = json.dumps(invoice_data['items'])
    
    db_invoice = Invoice(**invoice_data)
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    # Return with parsed items
    return {
        "id": db_invoice.id,
        "invoice_number": db_invoice.invoice_number,
        "client_id": db_invoice.client_id,
        "amount": db_invoice.amount,
        "status": db_invoice.status,
        "issue_date": db_invoice.issue_date,
        "due_date": db_invoice.due_date,
        "paid_date": db_invoice.paid_date,
        "items": json.loads(db_invoice.items) if db_invoice.items else [],
        "notes": db_invoice.notes,
        "created_at": db_invoice.created_at,
        "updated_at": db_invoice.updated_at
    }

@invoice_router.put("/{invoice_id}", response_model=Dict)
async def update_invoice(
    invoice_id: int,
    invoice: InvoiceUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Update an existing invoice."""
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    update_data = invoice.dict(exclude_unset=True)
    # Convert items list to JSON string if present
    if 'items' in update_data:
        update_data['items'] = json.dumps(update_data['items'])
    
    for field, value in update_data.items():
        setattr(db_invoice, field, value)
    
    db.commit()
    db.refresh(db_invoice)
    
    # Return with parsed items
    return {
        "id": db_invoice.id,
        "invoice_number": db_invoice.invoice_number,
        "client_id": db_invoice.client_id,
        "amount": db_invoice.amount,
        "status": db_invoice.status,
        "issue_date": db_invoice.issue_date,
        "due_date": db_invoice.due_date,
        "paid_date": db_invoice.paid_date,
        "items": json.loads(db_invoice.items) if db_invoice.items else [],
        "notes": db_invoice.notes,
        "created_at": db_invoice.created_at,
        "updated_at": db_invoice.updated_at
    }

@invoice_router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Delete an invoice."""
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    db.delete(db_invoice)
    db.commit()

@invoice_router.get("/client/{client_id}", response_model=List[Dict])
async def get_client_invoices(
    client_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get all invoices for a specific client."""
    invoices = db.query(Invoice).filter(Invoice.client_id == client_id).all()
    
    # Convert invoices to dict and parse JSON items
    invoice_list = []
    for invoice in invoices:
        invoice_dict = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "client_id": invoice.client_id,
            "amount": invoice.amount,
            "status": invoice.status,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "paid_date": invoice.paid_date,
            "items": json.loads(invoice.items) if invoice.items else [],
            "notes": invoice.notes,
            "created_at": invoice.created_at,
            "updated_at": invoice.updated_at
        }
        invoice_list.append(invoice_dict)
    
    return invoice_list

@invoice_router.get("/stats", response_model=Dict)
async def get_invoice_stats(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get invoice statistics."""
    total_invoices = db.query(Invoice).count()
    total_amount = db.query(func.sum(Invoice.amount)).scalar() or 0
    return {
        "total_invoices": total_invoices,
        "total_amount": total_amount
    }

# Payment endpoints
@payment_router.get("/", response_model=Dict)
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get all payments with pagination."""
    payments = db.query(Payment).offset(skip).limit(limit).all()
    total = db.query(Payment).count()
    
    # Convert payments to dict
    payment_list = []
    for payment in payments:
        payment_dict = {
            "id": payment.id,
            "amount": payment.amount,
            "status": payment.status,
            "method": payment.method,
            "transaction_id": payment.transaction_id,
            "payment_gateway_id": payment.payment_gateway_id,
            "currency": payment.currency,
            "project_id": payment.project_id,
            "client_id": payment.client_id,
            "invoice_id": payment.invoice_id,
            "payment_date": payment.payment_date,
            "notes": payment.notes,
            "created_at": payment.created_at,
            "updated_at": payment.updated_at
        }
        payment_list.append(payment_dict)
    
    return {"payments": payment_list, "total": total}

@payment_router.get("/{payment_id}", response_model=Dict)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific payment by ID."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return {
        "id": payment.id,
        "amount": payment.amount,
        "status": payment.status,
        "method": payment.method,
        "transaction_id": payment.transaction_id,
        "payment_gateway_id": payment.payment_gateway_id,
        "currency": payment.currency,
        "project_id": payment.project_id,
        "client_id": payment.client_id,
        "invoice_id": payment.invoice_id,
        "payment_date": payment.payment_date,
        "notes": payment.notes,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at
    }

@payment_router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new payment."""
    db_payment = Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@payment_router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment: PaymentUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Update an existing payment."""
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    for field, value in payment.dict(exclude_unset=True).items():
        setattr(db_payment, field, value)
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

@payment_router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a payment."""
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    db.delete(db_payment)
    db.commit()

@payment_router.get("/client/{client_id}", response_model=List[PaymentResponse])
async def get_client_payments(
    client_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for a specific client."""
    payments = db.query(Payment).filter(Payment.client_id == client_id).all()
    return payments

@payment_router.get("/invoice/{invoice_id}", response_model=List[PaymentResponse])
async def get_invoice_payments(
    invoice_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for a specific invoice."""
    payments = db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
    return payments

@payment_router.get("/stats", response_model=Dict)
async def get_payment_stats(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get payment statistics."""
    total_payments = db.query(Payment).count()
    total_amount = db.query(func.sum(Payment.amount)).scalar() or 0
    return {
        "total_payments": total_payments,
        "total_amount": total_amount
    }

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
