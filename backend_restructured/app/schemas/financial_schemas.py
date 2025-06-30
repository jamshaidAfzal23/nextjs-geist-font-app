"""
Financial schemas for Smart CRM SaaS application.
This module defines Pydantic models for payment, expense, and invoice data validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from ..models.financial_model import PaymentStatus, PaymentMethod, ExpenseCategory, InvoiceStatus

class PaymentBase(BaseModel):
    """
    Base payment schema with common fields.
    
    Attributes:
        amount (float): Payment amount
        status (PaymentStatus): Payment status
        method (PaymentMethod): Payment method used
        transaction_id (str): External payment reference
        notes (str): Additional payment notes
    """
    amount: float = Field(
        ...,
        gt=0,
        description="Payment amount"
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING,
        description="Current payment status"
    )
    method: PaymentMethod = Field(
        ...,
        description="Payment method used"
    )
    transaction_id: Optional[str] = Field(
        None,
        max_length=255,
        description="External payment system reference"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional payment notes"
    )

class PaymentCreate(PaymentBase):
    """Schema for creating a new payment."""
    project_id: int = Field(..., description="Associated project ID")
    client_id: int = Field(..., description="Client who made the payment")
    payment_date: Optional[datetime] = Field(None, description="When payment was made")

class PaymentUpdate(BaseModel):
    """
    Schema for updating payment information.
    
    All fields are optional for partial updates.
    """
    amount: Optional[float] = Field(None, gt=0)
    status: Optional[PaymentStatus] = None
    method: Optional[PaymentMethod] = None
    transaction_id: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=1000)
    payment_date: Optional[datetime] = None

class PaymentResponse(PaymentBase):
    """Schema for payment data in API responses."""
    id: int = Field(..., description="Unique payment identifier")
    project_id: int = Field(..., description="Associated project ID")
    client_id: int = Field(..., description="Client who made the payment")
    payment_date: Optional[datetime] = Field(None, description="Payment date")
    created_at: datetime
    updated_at: datetime
    
    # Related data
    project_title: Optional[str] = None
    client_name: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ExpenseBase(BaseModel):
    """
    Base expense schema with common fields.
    
    Attributes:
        title (str): Expense title/description
        amount (float): Expense amount
        category (ExpenseCategory): Type of expense
        notes (str): Additional expense notes
    """
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Expense title/description"
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Expense amount"
    )
    category: ExpenseCategory = Field(
        ...,
        description="Type of expense"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional expense notes"
    )

class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense."""
    linked_project_id: Optional[int] = Field(None, description="Associated project ID")
    created_by_id: int = Field(..., description="User who recorded the expense")
    receipt_url: Optional[str] = Field(None, description="URL to receipt image/document")
    expense_date: Optional[datetime] = Field(None, description="When expense occurred")

class ExpenseUpdate(BaseModel):
    """
    Schema for updating expense information.
    
    All fields are optional for partial updates.
    """
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[ExpenseCategory] = None
    notes: Optional[str] = Field(None, max_length=1000)
    receipt_url: Optional[str] = None
    expense_date: Optional[datetime] = None

class ExpenseResponse(ExpenseBase):
    """Schema for expense data in API responses."""
    id: int = Field(..., description="Unique expense identifier")
    linked_project_id: Optional[int] = Field(None, description="Associated project ID")
    created_by_id: int = Field(..., description="User who recorded the expense")
    receipt_url: Optional[str] = None
    expense_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Related data
    project_title: Optional[str] = None
    created_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InvoiceBase(BaseModel):
    """
    Base invoice schema with common fields.
    
    Attributes:
        invoice_number (str): Unique invoice identifier
        amount (float): Total invoice amount
        status (InvoiceStatus): Current invoice status
        items (List[Dict]): Invoice line items
        notes (str): Additional invoice notes
    """
    invoice_number: str = Field(
        ...,
        max_length=50,
        description="Unique invoice identifier"
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Total invoice amount"
    )
    status: InvoiceStatus = Field(
        default=InvoiceStatus.DRAFT,
        description="Current invoice status"
    )
    items: List[Dict] = Field(
        ...,
        description="Invoice line items"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional invoice notes"
    )

class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice."""
    client_id: int = Field(..., description="Client being billed")
    issue_date: datetime = Field(..., description="Invoice issue date")
    due_date: datetime = Field(..., description="Payment due date")

    @validator('due_date')
    def validate_due_date(cls, v, values):
        """Validate that due date is after issue date."""
        if 'issue_date' in values and v <= values['issue_date']:
            raise ValueError('Due date must be after issue date')
        return v

class InvoiceUpdate(BaseModel):
    """
    Schema for updating invoice information.
    
    All fields are optional for partial updates.
    """
    status: Optional[InvoiceStatus] = None
    amount: Optional[float] = Field(None, gt=0)
    items: Optional[List[Dict]] = None
    notes: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None

class InvoiceResponse(InvoiceBase):
    """Schema for invoice data in API responses."""
    id: int = Field(..., description="Unique invoice identifier")
    client_id: int = Field(..., description="Client being billed")
    issue_date: datetime = Field(..., description="Invoice issue date")
    due_date: datetime = Field(..., description="Payment due date")
    paid_date: Optional[datetime] = Field(None, description="When invoice was paid")
    created_at: datetime
    updated_at: datetime
    
    # Related data
    client_name: Optional[str] = None
    is_overdue: Optional[bool] = None
    days_until_due: Optional[int] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FinancialStats(BaseModel):
    """Schema for financial statistics and analytics."""
    total_revenue: float = Field(..., description="Total revenue from all payments")
    total_expenses: float = Field(..., description="Total expenses")
    net_profit: float = Field(..., description="Net profit (revenue - expenses)")
    profit_margin: float = Field(..., description="Profit margin percentage")
    revenue_by_month: Dict[str, float] = Field(..., description="Monthly revenue breakdown")
    expenses_by_category: Dict[str, float] = Field(..., description="Expenses by category")
    outstanding_invoices: float = Field(..., description="Total amount in unpaid invoices")
    average_payment_time: Optional[float] = Field(None, description="Average days to payment")
