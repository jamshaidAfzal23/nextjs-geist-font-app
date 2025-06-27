from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserBase(BaseModel):
    name: str
    email: str
    role: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class ClientBase(BaseModel):
    name: str
    contact_info: Optional[str] = None
    platform: Optional[str] = None
    user_id: int

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    title: str
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    client_id: int
    developer_id: int

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int

    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    project_id: int
    amount: float
    payment_type: Optional[str] = None
    date: Optional[date] = None
    profit_split_ratio: Optional[float] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int

    class Config:
        orm_mode = True

class ExpenseBase(BaseModel):
    title: str
    category: Optional[str] = None
    amount: float
    linked_project_id: Optional[int] = None
    platform: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int

    class Config:
        orm_mode = True

class InvoiceBase(BaseModel):
    client_id: int
    amount: float
    issue_date: Optional[date] = None
    pdf_url: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int

    class Config:
        orm_mode = True

class AILogBase(BaseModel):
    action_type: str
    related_entity: Optional[str] = None
    generated_output: Optional[str] = None

class AILogCreate(AILogBase):
    pass

class AILog(AILogBase):
    id: int

    class Config:
        orm_mode = True
