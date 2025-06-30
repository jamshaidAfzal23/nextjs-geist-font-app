"""
Financial API endpoints for Smart CRM SaaS application.
This module defines all financial-related API routes including payments,
expenses, invoices, and financial analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from ...core.database import get_database_session
from ...core.rbac import check_permissions
from ...models import Payment, Expense, Invoice, Project, Client, User
from ...models.financial_model import PaymentStatus, ExpenseCategory, InvoiceStatus
from ...schemas import (
    PaymentCreate, PaymentUpdate, PaymentResponse,
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    FinancialStats
)

# Create separate routers for each financial entity
payment_router = APIRouter(prefix="/payments", tags=["payments"])
expense_router = APIRouter(prefix="/expenses", tags=["expenses"])
invoice_router = APIRouter(prefix="/invoices", tags=["invoices"])
financial_router = APIRouter(prefix="/financial", tags=["financial-analytics"])

# PAYMENT ENDPOINTS
@payment_router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["payments:create"]))])
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_database_session)
):
    """
    Create a new payment record.
    
    Args:
        payment_data (PaymentCreate): Payment creation data
        db (Session): Database session
        
    Returns:
        PaymentResponse: Created payment information
        
    Raises:
        HTTPException: If project or client not found
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == payment_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Verify client exists
    client = db.query(Client).filter(Client.id == payment_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Create new payment
    db_payment = Payment(**payment_data.dict())
    if not db_payment.payment_date:
        db_payment.payment_date = datetime.now()
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return db_payment

@payment_router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    date_from: Optional[datetime] = Query(None, description="Filter payments from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter payments to this date"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a list of payments with optional filtering.
    
    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        project_id (int, optional): Filter by project ID
        client_id (int, optional): Filter by client ID
        status (PaymentStatus, optional): Filter by payment status
        date_from (datetime, optional): Filter payments from this date
        date_to (datetime, optional): Filter payments to this date
        db (Session): Database session
        
    Returns:
        List[PaymentResponse]: List of payments
    """
    query = db.query(Payment)
    
    if project_id:
        query = query.filter(Payment.project_id == project_id)
    
    if client_id:
        query = query.filter(Payment.client_id == client_id)
    
    if status:
        query = query.filter(Payment.status == status)
    
    if date_from:
        query = query.filter(Payment.payment_date >= date_from)
    
    if date_to:
        query = query.filter(Payment.payment_date <= date_to)
    
    payments = query.offset(skip).limit(limit).all()
    
    # Enhance with related data
    enhanced_payments = []
    for payment in payments:
        payment_dict = payment.__dict__.copy()
        if payment.project:
            payment_dict['project_title'] = payment.project.title
        if payment.client:
            payment_dict['client_name'] = payment.client.company_name
        enhanced_payments.append(payment_dict)
    
    return enhanced_payments

@payment_router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a specific payment by ID.
    
    Args:
        payment_id (int): Payment ID to retrieve
        db (Session): Database session
        
    Returns:
        PaymentResponse: Payment information
        
    Raises:
        HTTPException: If payment not found
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment

@payment_router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_database_session)
):
    """
    Update payment information.
    
    Args:
        payment_id (int): Payment ID to update
        payment_data (PaymentUpdate): Updated payment data
        db (Session): Database session
        
    Returns:
        PaymentResponse: Updated payment information
        
    Raises:
        HTTPException: If payment not found
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    update_data = payment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)
    
    db.commit()
    db.refresh(payment)
    
    return payment

# EXPENSE ENDPOINTS
@expense_router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["expenses:create"]))])
async def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_database_session)
):
    """
    Create a new expense record.
    
    Args:
        expense_data (ExpenseCreate): Expense creation data
        db (Session): Database session
        
    Returns:
        ExpenseResponse: Created expense information
        
    Raises:
        HTTPException: If project or user not found
    """
    # Verify project exists (if provided)
    if expense_data.linked_project_id:
        project = db.query(Project).filter(Project.id == expense_data.linked_project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    # Verify user exists
    user = db.query(User).filter(User.id == expense_data.created_by_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create new expense
    db_expense = Expense(**expense_data.dict())
    if not db_expense.expense_date:
        db_expense.expense_date = datetime.now()
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

@expense_router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    category: Optional[ExpenseCategory] = Query(None, description="Filter by expense category"),
    created_by_id: Optional[int] = Query(None, description="Filter by user who created expense"),
    date_from: Optional[datetime] = Query(None, description="Filter expenses from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter expenses to this date"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a list of expenses with optional filtering.
    
    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        project_id (int, optional): Filter by project ID
        category (ExpenseCategory, optional): Filter by expense category
        created_by_id (int, optional): Filter by user who created expense
        date_from (datetime, optional): Filter expenses from this date
        date_to (datetime, optional): Filter expenses to this date
        db (Session): Database session
        
    Returns:
        List[ExpenseResponse]: List of expenses
    """
    query = db.query(Expense)
    
    if project_id:
        query = query.filter(Expense.linked_project_id == project_id)
    
    if category:
        query = query.filter(Expense.category == category)
    
    if created_by_id:
        query = query.filter(Expense.created_by_id == created_by_id)
    
    if date_from:
        query = query.filter(Expense.expense_date >= date_from)
    
    if date_to:
        query = query.filter(Expense.expense_date <= date_to)
    
    expenses = query.offset(skip).limit(limit).all()
    
    # Enhance with related data
    enhanced_expenses = []
    for expense in expenses:
        expense_dict = expense.__dict__.copy()
        if expense.linked_project:
            expense_dict['project_title'] = expense.linked_project.title
        if expense.created_by_user:
            expense_dict['created_by_name'] = expense.created_by_user.full_name
        enhanced_expenses.append(expense_dict)
    
    return enhanced_expenses

@expense_router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a specific expense by ID.
    
    Args:
        expense_id (int): Expense ID to retrieve
        db (Session): Database session
        
    Returns:
        ExpenseResponse: Expense information
        
    Raises:
        HTTPException: If expense not found
    """
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    return expense

# INVOICE ENDPOINTS
@invoice_router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["invoices:create"]))])
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_database_session)
):
    """
    Create a new invoice.
    
    Args:
        invoice_data (InvoiceCreate): Invoice creation data
        db (Session): Database session
        
    Returns:
        InvoiceResponse: Created invoice information
        
    Raises:
        HTTPException: If client not found or invoice number already exists
    """
    # Verify client exists
    client = db.query(Client).filter(Client.id == invoice_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check if invoice number already exists
    existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_data.invoice_number).first()
    if existing_invoice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice number already exists"
        )
    
    # Create new invoice
    db_invoice = Invoice(**invoice_data.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return db_invoice

@invoice_router.get("/", response_model=List[InvoiceResponse])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    overdue_only: Optional[bool] = Query(False, description="Show only overdue invoices"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a list of invoices with optional filtering.
    
    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        client_id (int, optional): Filter by client ID
        status (InvoiceStatus, optional): Filter by invoice status
        overdue_only (bool): Show only overdue invoices
        db (Session): Database session
        
    Returns:
        List[InvoiceResponse]: List of invoices
    """
    query = db.query(Invoice)
    
    if client_id:
        query = query.filter(Invoice.client_id == client_id)
    
    if status:
        query = query.filter(Invoice.status == status)
    
    if overdue_only:
        current_date = datetime.now()
        query = query.filter(
            Invoice.due_date < current_date,
            Invoice.status != InvoiceStatus.PAID
        )
    
    invoices = query.offset(skip).limit(limit).all()
    
    # Enhance with computed fields
    enhanced_invoices = []
    for invoice in invoices:
        invoice_dict = invoice.__dict__.copy()
        if invoice.client:
            invoice_dict['client_name'] = invoice.client.company_name
        
        # Calculate if overdue
        current_date = datetime.now()
        invoice_dict['is_overdue'] = (
            invoice.due_date < current_date and 
            invoice.status != InvoiceStatus.PAID
        )
        
        # Calculate days until due
        if invoice.due_date:
            days_diff = (invoice.due_date - current_date).days
            invoice_dict['days_until_due'] = days_diff
        
        enhanced_invoices.append(invoice_dict)
    
    return enhanced_invoices

# FINANCIAL ANALYTICS ENDPOINTS
@financial_router.get("/stats", response_model=FinancialStats)
async def get_financial_stats(
    year: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_database_session)
):
    """
    Get comprehensive financial statistics.
    
    Args:
        year (int, optional): Filter statistics by year
        db (Session): Database session
        
    Returns:
        FinancialStats: Financial analytics and statistics
    """
    # Set date filters
    if year:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
    else:
        # Current year
        current_year = datetime.now().year
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31, 23, 59, 59)
    
    # Calculate total revenue
    total_revenue = db.query(func.sum(Payment.amount))\
        .filter(
            Payment.status == PaymentStatus.COMPLETED,
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).scalar() or 0.0
    
    # Calculate total expenses
    total_expenses = db.query(func.sum(Expense.amount))\
        .filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).scalar() or 0.0
    
    # Calculate net profit and margin
    net_profit = total_revenue - total_expenses
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Revenue by month
    revenue_by_month = {}
    monthly_revenue = db.query(
        extract('month', Payment.payment_date).label('month'),
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.status == PaymentStatus.COMPLETED,
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).group_by(extract('month', Payment.payment_date)).all()
    
    for month, total in monthly_revenue:
        month_name = datetime(2000, int(month), 1).strftime('%B')
        revenue_by_month[month_name] = float(total)
    
    # Expenses by category
    expenses_by_category = {}
    category_expenses = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).group_by(Expense.category).all()
    
    for category, total in category_expenses:
        expenses_by_category[category] = float(total)
    
    # Outstanding invoices
    outstanding_invoices = db.query(func.sum(Invoice.amount))\
        .filter(Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.OVERDUE]))\
        .scalar() or 0.0
    
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

# Combine all financial routers
financial_main_router = APIRouter()
financial_main_router.include_router(payment_router)
financial_main_router.include_router(expense_router)
financial_main_router.include_router(invoice_router)
financial_main_router.include_router(financial_router)
