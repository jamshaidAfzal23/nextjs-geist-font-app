"""User Preference model for the Smart CRM SaaS application."""

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from ..core.database import Base

class UserPreference(Base):
    """User preferences model for storing user-specific settings."""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = Column(String, default="light")
    notifications_enabled = Column(Boolean, default=True)
    dashboard_layout = Column(String, default="default")
    custom_settings = Column(JSON, default={})

    # Relationship back to user
    user = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        """String representation of UserPreference object."""
        return f"<UserPreference(user_id={self.user_id}, theme='{self.theme}')>"
