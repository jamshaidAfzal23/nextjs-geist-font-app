"""
Financial models for Smart CRM SaaS application.
This module defines the Payment, Expense, and Invoice database models and related functionality.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..core.database import Base

class PaymentStatus(str, PyEnum):
    """Enumeration of possible payment statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, PyEnum):
    """Enumeration of supported payment methods."""
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    CRYPTO = "cryptocurrency"

class Payment(Base):
    """
    Payment model representing financial transactions from clients.
    
    Attributes:
        id (int): Primary key
        amount (float): Payment amount
        status (PaymentStatus): Current payment status
        method (PaymentMethod): Payment method used
        transaction_id (str): External payment system reference
        project_id (int): Associated project ID
        client_id (int): Client who made the payment
        payment_date (datetime): When payment was made
        notes (Text): Additional payment notes
    """
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default=PaymentStatus.PENDING
    )
    method = Column(String(50), nullable=False)
    transaction_id = Column(String(255), unique=True)
    
    project_id = Column(Integer, ForeignKey("projects.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    payment_date = Column(DateTime(timezone=True))
    notes = Column(Text)
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    project = relationship("Project", back_populates="payments")
    client = relationship("Client", back_populates="payments")

class ExpenseCategory(str, PyEnum):
    """Enumeration of expense categories."""
    SOFTWARE = "software"
    HARDWARE = "hardware"
    SERVICES = "services"
    MARKETING = "marketing"
    TRAVEL = "travel"
    OTHER = "other"

class Expense(Base):
    """
    Expense model representing project-related expenses.
    
    Attributes:
        id (int): Primary key
        title (str): Expense title/description
        amount (float): Expense amount
        category (ExpenseCategory): Type of expense
        linked_project_id (int): Associated project
        created_by_id (int): User who recorded the expense
        receipt_url (str): URL to receipt image/document
        notes (Text): Additional expense notes
    """
    
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(
        String(50),
        nullable=False,
        default=ExpenseCategory.OTHER
    )
    
    linked_project_id = Column(Integer, ForeignKey("projects.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    receipt_url = Column(String(500))
    notes = Column(Text)
    
    expense_date = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    linked_project = relationship("Project", back_populates="expenses")
    created_by_user = relationship("User", back_populates="created_expenses")

class InvoiceStatus(str, PyEnum):
    """Enumeration of possible invoice statuses."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Invoice(Base):
    """
    Invoice model representing billing documents sent to clients.
    
    Attributes:
        id (int): Primary key
        invoice_number (str): Unique invoice identifier
        client_id (int): Client being billed
        amount (float): Total invoice amount
        status (InvoiceStatus): Current invoice status
        due_date (datetime): Payment due date
        items (Text): JSON string of invoice line items
        notes (Text): Additional invoice notes
    """
    
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    amount = Column(Float, nullable=False)
    status = Column(
        String(50),
        nullable=False,
        default=InvoiceStatus.DRAFT
    )
    
    issue_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    paid_date = Column(DateTime(timezone=True))
    
    items = Column(Text)  # JSON string of invoice items
    notes = Column(Text)
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    client = relationship("Client", back_populates="invoices")
    
    def __repr__(self) -> str:
        """String representation of the Invoice object."""
        return f"<Invoice(number='{self.invoice_number}', amount={self.amount}, status='{self.status}')>"
    
    def __str__(self) -> str:
        """Human-readable string representation of the Invoice object."""
        return f"Invoice #{self.invoice_number} - {self.status}"
