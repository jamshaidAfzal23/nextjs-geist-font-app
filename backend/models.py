from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Text
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)

    clients = relationship("Client", back_populates="user")
    projects = relationship("Project", back_populates="developer")

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_info = Column(String)
    platform = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="clients")
    projects = relationship("Project", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    client_id = Column(Integer, ForeignKey("clients.id"))
    developer_id = Column(Integer, ForeignKey("users.id"))

    client = relationship("Client", back_populates="projects")
    developer = relationship("User", back_populates="projects")
    payments = relationship("Payment", back_populates="project")
    expenses = relationship("Expense", back_populates="linked_project")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    amount = Column(Float, nullable=False)
    payment_type = Column(String)
    date = Column(Date)
    profit_split_ratio = Column(Float)

    project = relationship("Project", back_populates="payments")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String)
    amount = Column(Float, nullable=False)
    linked_project_id = Column(Integer, ForeignKey("projects.id"))
    platform = Column(String)

    linked_project = relationship("Project", back_populates="expenses")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    amount = Column(Float, nullable=False)
    issue_date = Column(Date)
    pdf_url = Column(String)

    client = relationship("Client", back_populates="invoices")

class AILog(Base):
    __tablename__ = "ai_logs"
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String)
    related_entity = Column(String)  # Could be client or project identifier
    generated_output = Column(Text)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    permissions = Column(String)  # Comma-separated permissions list
