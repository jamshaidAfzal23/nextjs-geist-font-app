from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy.orm import Session

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Client CRUD
def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(
        name=client.name,
        contact_info=client.contact_info,
        platform=client.platform,
        user_id=client.user_id,
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# Project CRUD
def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        title=project.title,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        client_id=project.client_id,
        developer_id=project.developer_id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# Payment CRUD
def get_payment(db: Session, payment_id: int):
    return db.query(models.Payment).filter(models.Payment.id == payment_id).first()

def get_payments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Payment).offset(skip).limit(limit).all()

def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(
        project_id=payment.project_id,
        amount=payment.amount,
        payment_type=payment.payment_type,
        date=payment.date,
        profit_split_ratio=payment.profit_split_ratio,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

# Expense CRUD
def get_expense(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def get_expenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Expense).offset(skip).limit(limit).all()

def create_expense(db: Session, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(
        title=expense.title,
        category=expense.category,
        amount=expense.amount,
        linked_project_id=expense.linked_project_id,
        platform=expense.platform,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

# Additional CRUD functions for Invoice and AILog can be added similarly
