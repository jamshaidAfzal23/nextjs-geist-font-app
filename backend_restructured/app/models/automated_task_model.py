"""
Automated Task model for the Smart CRM SaaS application.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base

class AutomatedTask(Base):
    __tablename__ = "automated_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String, nullable=False)  # e.g., 'reminder', 'follow_up', 'report_generation'
    scheduled_time = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    target_id = Column(Integer, nullable=True)  # e.g., client_id, project_id, user_id
    target_type = Column(String, nullable=True) # e.g., 'client', 'project', 'user'
    details = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_by_user = relationship("User")
