"""
Report Template model for the Smart CRM SaaS application.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base

class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    template_type = Column(String, nullable=False)  # e.g., 'financial', 'client', 'project'
    template_content = Column(Text, nullable=False)  # JSON or other format defining the template structure
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
