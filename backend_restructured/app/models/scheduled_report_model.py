"""
Scheduled Report model for the Smart CRM SaaS application.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base

class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_name = Column(String, nullable=False)
    report_type = Column(String, nullable=False)  # e.g., 'financial', 'client', 'project'
    schedule_interval = Column(String, nullable=False)  # e.g., 'daily', 'weekly', 'monthly'
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=False)
    recipients = Column(Text, nullable=False)  # Comma-separated emails or user IDs
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
