"""
API endpoints for managing client history.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.client_history_model import ClientHistory
from ...schemas.client_history_schemas import ClientHistoryResponse

router = APIRouter()


@router.get("/{client_id}/history", response_model=List[ClientHistoryResponse])
async def get_client_history(
    client_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get the history of a specific client."""
    history = db.query(ClientHistory).filter(ClientHistory.client_id == client_id).offset(skip).limit(limit).all()
    return history
