"""
User Preference model for the Smart CRM SaaS application.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from ..core.database import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    theme = Column(String, default="light")
    notifications_enabled = Column(Boolean, default=True)

    user = relationship("User", back_populates="preferences")
