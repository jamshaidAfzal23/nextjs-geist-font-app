"""Client note model for managing notes and comments about clients."""

from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class ClientNote(Base):
    """Model for storing notes and comments about clients.
    
    This model allows users to maintain detailed notes about client interactions,
    meetings, requirements, and other important information.
    
    Attributes:
        id (int): Primary key
        client_id (int): Foreign key to the client
        user_id (int): Foreign key to the user who created the note
        content (Text): The actual note content
        note_type (str): Type of note (e.g., 'meeting', 'call', 'email')
        is_important (bool): Flag for important notes
        is_private (bool): Flag for private notes visible only to creator
        created_at (datetime): When the note was created
        updated_at (datetime): When the note was last updated
    """
    
    __tablename__ = "client_notes"
    
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
    content = Column(
        Text,
        nullable=False,
        doc="The actual note content"
    )
    note_type = Column(
        String(50),
        nullable=False,
        default="general",
        doc="Type of note: meeting, call, email, general, etc."
    )
    is_important = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Flag for marking important notes"
    )
    is_private = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Flag for private notes visible only to creator"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    client = relationship(
        "Client",
        back_populates="notes_list",
        doc="Reference to the client this note belongs to"
    )
    user = relationship(
        "User",
        doc="Reference to the user who created this note"
    )
    
    def __repr__(self) -> str:
        """String representation of the ClientNote object."""
        return f"<ClientNote(id={self.id}, client_id={self.client_id}, type='{self.note_type}')>"
    
    @property
    def summary(self) -> str:
        """Get a short summary of the note content.
        
        Returns:
            str: First 100 characters of the note content
        """
        return (self.content[:97] + '...') if len(self.content) > 100 else self.content