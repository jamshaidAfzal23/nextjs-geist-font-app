"""Client history model for tracking changes in client information."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class ClientHistory(Base):
    """Model for tracking historical changes to client information.
    
    This model maintains an audit trail of changes made to client records,
    including what was changed, when it was changed, and who made the change.
    
    Attributes:
        id (int): Primary key
        client_id (int): Foreign key to the client
        user_id (int): Foreign key to the user who made the change
        change_type (str): Type of change (e.g., 'update', 'create', 'delete')
        field_name (str): Name of the field that was changed
        old_value (JSON): Previous value of the field
        new_value (JSON): New value of the field
        timestamp (datetime): When the change occurred
        notes (Text): Additional notes about the change
    """
    
    __tablename__ = "client_history"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    change_type = Column(
        String(50),
        nullable=False,
        doc="Type of change: create, update, delete"
    )
    field_name = Column(
        String(100),
        nullable=True,
        doc="Name of the field that was changed"
    )
    old_value = Column(
        JSON,
        nullable=True,
        doc="Previous value of the field"
    )
    new_value = Column(
        JSON,
        nullable=True,
        doc="New value of the field"
    )
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    notes = Column(
        Text,
        nullable=True,
        doc="Additional context about the change"
    )
    
    # Relationships
    client = relationship(
        "Client",
        back_populates="history",
        doc="Reference to the client this history entry belongs to"
    )
    user = relationship(
        "User",
        doc="Reference to the user who made this change"
    )
    
    def __repr__(self) -> str:
        """String representation of the ClientHistory object."""
        return f"<ClientHistory(id={self.id}, client_id={self.client_id}, change_type='{self.change_type}')>"