"""
API endpoints for managing client notes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.client_model import Client
from ...models.client_note_model import ClientNote
from ...schemas.client_note_schemas import ClientNoteCreate, ClientNoteResponse

router = APIRouter()


@router.post("/{client_id}/notes", response_model=ClientNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_client_note(
    client_id: int,
    note_data: ClientNoteCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new note for a specific client.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db_note = ClientNote(
        client_id=client_id,
        user_id=current_user.id,
        content=note_data.content
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("/{client_id}/notes", response_model=List[ClientNoteResponse])
async def get_client_notes(
    client_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get all notes for a specific client.
    """
    notes = db.query(ClientNote).filter(ClientNote.client_id == client_id).offset(skip).limit(limit).all()
    return notes


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_note(
    note_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific client note.
    """
    note = db.query(ClientNote).filter(ClientNote.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Add authorization: only the note creator or an admin can delete
    if note.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this note"
        )

    db.delete(note)
    db.commit()
