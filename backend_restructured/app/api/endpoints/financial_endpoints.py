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
    sort_order: Optional[str] = Query("asc", description="Sort order ('asc' or 'desc')"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response (e.g., 'id,amount,status')"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a list of payments with optional filtering, sorting, and field selection.
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
    
    # Apply sorting
    if sort_by:
        if hasattr(Payment, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(Payment, sort_by).desc())
            else:
                query = query.order_by(getattr(Payment, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    payments = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        processed_payments = []
        for payment in payments:
            payment_dict = payment.__dict__.copy()
            filtered_payment = {k: v for k, v in payment_dict.items() if k in selected_fields}
            processed_payments.append(filtered_payment)
        payments = processed_payments
    else:
        # Enhance with related data
        enhanced_payments = []
        for payment in payments:
            payment_dict = payment.__dict__.copy()
            if payment.project:
                payment_dict['project_title'] = payment.project.title
            if payment.client:
                payment_dict['client_name'] = payment.client.company_name
            enhanced_payments.append(payment_dict)
        payments = enhanced_payments
    
    return payments

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

@payment_router.post("/bulk", response_model=List[PaymentResponse], status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["payments:create"]))])
async def create_multiple_payments(
    payments_data: PaymentCreateBulk,
    db: Session = Depends(get_database_session)
):
    """
    Create multiple payment records in a single request.
    """
    created_payments = []
    for payment_data in payments_data.payments:
        db_payment = Payment(**payment_data.dict())
        db.add(db_payment)
        created_payments.append(db_payment)
    
    db.commit()
    for payment in created_payments:
        db.refresh(payment)
    
    return created_payments


@payment_router.put("/bulk", response_model=List[PaymentResponse], status_code=status.HTTP_200_OK, dependencies=[Depends(check_permissions(["payments:update"]))])
async def update_multiple_payments(
    payments_data: PaymentUpdateBulk,
    db: Session = Depends(get_database_session)
):
    """
    Update multiple payment records in a single request.
    """
    updated_payments = []
    for payment_data in payments_data.payments:
        payment = db.query(Payment).filter(Payment.id == payment_data.id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_data.id} not found"
            )
        
        for field, value in payment_data.dict(exclude_unset=True).items():
            setattr(payment, field, value)
        updated_payments.append(payment)
    
    db.commit()
    for payment in updated_payments:
        db.refresh(payment)
    
    return updated_payments


@payment_router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(check_permissions(["payments:delete"]))])
async def delete_multiple_payments(
    payment_ids_data: PaymentDeleteBulk,
    db: Session = Depends(get_database_session)
):
    """
    Delete multiple payment records in a single request.
    """
    for payment_id in payment_ids_data.payment_ids:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_id} not found"
            )
        db.delete(payment)
    
    db.commit()

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
    sort_order: Optional[str] = Query("asc", description="Sort order ('asc' or 'desc')"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response (e.g., 'id,title,amount')"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a list of expenses with optional filtering, sorting, and field selection.
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
    
    # Apply sorting
    if sort_by:
        if hasattr(Expense, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(Expense, sort_by).desc())
            else:
                query = query.order_by(getattr(Expense, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    expenses = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        processed_expenses = []
        for expense in expenses:
            expense_dict = expense.__dict__.copy()
            filtered_expense = {k: v for k, v in expense_dict.items() if k in selected_fields}
            processed_expenses.append(filtered_expense)
        expenses = processed_expenses
    else:
        # Enhance with related data
        enhanced_expenses = []
        for expense in expenses:
            expense_dict = expense.__dict__.copy()
            if expense.linked_project:
                expense_dict['project_title'] = expense.linked_project.title
            if expense.created_by_user:
                expense_dict['created_by_name'] = expense.created_by_user.full_name
            enhanced_expenses.append(expense_dict)
        expenses = enhanced_expenses
    
    return enhanced_expenses
    """
    Retrieve a list of expenses with optional filtering, sorting, and field selection.
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
    
    # Apply sorting
    if sort_by:
        if hasattr(Expense, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(Expense, sort_by).desc())
            else:
                query = query.order_by(getattr(Expense, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    expenses = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        processed_expenses = []
        for expense in expenses:
            expense_dict = expense.__dict__.copy()
            filtered_expense = {k: v for k, v in expense_dict.items() if k in selected_fields}
            processed_expenses.append(filtered_expense)
        expenses = processed_expenses
    else:
        # Enhance with related data
        enhanced_expenses = []
        for expense in expenses:
            expense_dict = expense.__dict__.copy()
            if expense.linked_project:
                expense_dict['project_title'] = expense.linked_project.title
            if expense.created_by_user:
                expense_dict['created_by_name'] = expense.created_by_user.full_name
            enhanced_expenses.append(expense_dict)
        expenses = enhanced_expenses
    
    return enhanced_expenses
    """
    Retrieve a list of expenses with optional filtering, sorting, and field selection.
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
    
    # Apply sorting
    if sort_by:
        if hasattr(Expense, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(Expense, sort_by).desc())
            else:
                query = query.order_by(getattr(Expense, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    expenses = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        processed_expenses = []
        for expense in expenses:
            expense_dict = expense.__dict__.copy()
            filtered_expense = {k: v for k, v in expense_dict.items() if k in selected_fields}
            processed_expenses.append(filtered_expense)
        expenses = processed_expenses
    else:
        # Enhance with related data
        enhanced_expenses = []
        for expense in expenses:
            expense_dict = expense.__dict__.copy()
            if expense.linked_project:
                expense_dict['project_title'] = expense.linked_project.title
            if expense.created_by_user:
                expense_dict['created_by_name'] = expense.created_by_user.full_name
            enhanced_expenses.append(expense_dict)
        expenses = enhanced_expenses
    
    return enhanced_expenses
    """
    Retrieve a list of expenses with optional filtering, sorting, and field selection.
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
    
    # Apply sorting
    if sort_by:
        if hasattr(Expense, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(Expense, sort_by).desc())
            else:
                query = query.order_by(getattr(Expense, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    expenses = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        processed_expenses = []
        for expense in expenses:
            expense_dict = expense.__dict__.copy()
            filtered_expense = {k: v for k, v in expense_dict.items() if k in selected_fields}
            processed_expenses.append(filtered_expense)
        expenses = processed_expenses
    else:
        # Enhance with related data
        enhanced_expenses = []
        for expense in expenses:
            expense_dict = expense.__dict__.copy()
            if expense.linked_project:
                expense_dict['project_title'] = expense.linked_project.title
            if expense.created_by_user:
                expense_dict['created_by_name'] = expense.created_by_user.full_name
            enhanced_expenses.append(expense_dict)
        expenses = enhanced_expenses
    
    return enhanced_expenses

@expense_router.post("/bulk", response_model=List[ExpenseResponse], status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["expenses:create"]))])
async def create_multiple_expenses(
    expenses_data: ExpenseCreateBulk,
    db: Session = Depends(get_database_session)
):
    """
    Create multiple expense records in a single request.
    """
    created_expenses = []
    for expense_data in expenses_data.expenses:
        db_expense = Expense(**expense_data.dict())
        db.add(db_expense)
        created_expenses.append(db_expense)
    
    db.commit()
    for expense in created_expenses:
        db.refresh(expense)
    
    return created_expenses


@expense_router.put("/bulk", response_model=List[ExpenseResponse], status_code=status.HTTP_200_OK, dependencies=[Depends(check_permissions(["expenses:update"]))])
async def update_multiple_expenses(
    expenses_data: ExpenseUpdateBulk,
    db: Session = Depends(get_database_session)
):
    """
    Update multiple expense records in a single request.
    """
    updated_expenses = []
    for expense_data in expenses_data.expenses:
        expense = db.query(Expense).filter(Expense.id == expense_data.id).first()
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with ID {expense_data.id} not found"
            )
        
        for field, value in expense_data.dict(exclude_unset=True).items():
            setattr(expense, field, value)
        updated_expenses.append(expense)
    
    db.commit()
    for expense in updated_expenses:
        db.refresh(expense)
    
    return updated_expenses


@expense_router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(check_permissions(["expenses:delete"]))])
async def delete_multiple_expenses(
    expense_ids_data: ExpenseDeleteBulk,
    db: Session = Depends(get_database_session)
):
    """
    Delete multiple expense records in a single request.
    """
    for expense_id in expense_ids_data.expense_ids:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with ID {expense_id} not found"
            )
        db.delete(expense)
    
    db.commit()

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


@invoice_router.post("/bulk", response_model=List[InvoiceResponse], status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["invoices:create"]))])
async def create_multiple_invoices(
    invoices_data: InvoiceCreateBulk,
    db: Session = Depends(get_database_session)
):
    """
    Create multiple invoice records in a single request.
    """
    created_invoices = []
    for invoice_data in invoices_data.invoices:
        client = db.query(Client).filter(Client.id == invoice_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {invoice_data.client_id} not found for invoice"
            )
        existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_data.invoice_number).first()
        if existing_invoice:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invoice number {invoice_data.invoice_number} already exists"
            )
        db_invoice = Invoice(**invoice_data.dict())
        db.add(db_invoice)
        created_invoices.append(db_invoice)
    
    db.commit()
    for invoice in created_invoices:
        db.refresh(invoice)
    
    return created_invoices


@invoice_router.put("/bulk", response_model=List[InvoiceResponse], status_code=status.HTTP_200_OK, dependencies=[Depends(check_permissions(["invoices:update"]))])
async def update_multiple_invoices(
    invoices_data: InvoiceUpdateBulk,
    db: Session = Depends(get_database_session)
):
    """
    Update multiple invoice records in a single request.
    """
    updated_invoices = []
    for invoice_data in invoices_data.invoices:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_data.id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice with ID {invoice_data.id} not found"
            )
        for field, value in invoice_data.dict(exclude_unset=True).items():
            setattr(invoice, field, value)
        updated_invoices.append(invoice)
    
    db.commit()
    for invoice in updated_invoices:
        db.refresh(invoice)
    
    return updated_invoices


@invoice_router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(check_permissions(["invoices:delete"]))])
async def delete_multiple_invoices(
    invoice_ids_data: InvoiceDeleteBulk,
    db: Session = Depends(get_database_session)
):
    """
    Delete multiple invoice records in a single request.
    """
    for invoice_id in invoice_ids_data.invoice_ids:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice with ID {invoice_id} not found"
            )
        db.delete(invoice)
    
    db.commit()

@invoice_router.get("/", response_model=List[InvoiceResponse])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    status: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    overdue_only: Optional[bool] = Query(False, description="Show only overdue invoices"),
    sort_order: Optional[str] = Query("asc", description="Sort order ('asc' or 'desc')"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response (e.g., 'id,invoice_number,amount')"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a list of invoices with optional filtering, sorting, and field selection.
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
    
    # Apply sorting
    if sort_by:
        if hasattr(Invoice, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(Invoice, sort_by).desc())
            else:
                query = query.order_by(getattr(Invoice, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    invoices = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        processed_invoices = []
        for invoice in invoices:
            invoice_dict = invoice.__dict__.copy()
            filtered_invoice = {k: v for k, v in invoice_dict.items() if k in selected_fields}
            processed_invoices.append(filtered_invoice)
        invoices = processed_invoices
    else:
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
        invoices = enhanced_invoices
    
    return invoices

@invoice_router.get("/{invoice_id}/generate-pdf", status_code=status.HTTP_200_OK)
async def generate_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a PDF for a specific invoice.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # In a real application, you would use a PDF generation library (e.g., ReportLab, WeasyPrint)
    # to create the PDF from invoice data.
    # For now, this is a placeholder.
    
    return {"message": f"PDF generation for invoice {invoice_id} is not yet implemented."}

# FINANCIAL ANALYTICS ENDPOINTS
@financial_router.get("/stats", response_model=FinancialStats)
async def get_financial_stats(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_database_session)
):
    """
    Get comprehensive financial statistics.
    
    Args:
        year (int, optional): Filter statistics by year
        month (int, optional): Filter statistics by month
        client_id (int, optional): Filter by client ID
        project_id (int, optional): Filter by project ID
        db (Session): Database session
        
    Returns:
        FinancialStats: Financial analytics and statistics
    """
    # Set date filters
    if year and month:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, 1) + timedelta(days=32) # Go to next month and subtract a day
        end_date = end_date.replace(day=1) - timedelta(days=1)
    elif year:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
    else:
        # Current year
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

# Combine all financial routers
financial_main_router = APIRouter()
financial_main_router.include_router(payment_router)
financial_main_router.include_router(expense_router)
financial_main_router.include_router(invoice_router)
financial_main_router.include_router(financial_router)
