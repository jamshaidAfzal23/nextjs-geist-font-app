"""
API endpoints for managing API keys.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...services.api_key_service import create_api_key, get_api_key, revoke_api_key

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def generate_api_key(db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
    """Generate a new API key for the current user."""
    api_key = create_api_key(db, current_user.id)
    return {"api_key": api_key.key}


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_existing_api_key(key: str, db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
    """Revoke an API key."""
    api_key = get_api_key(db, key)
    if not api_key or api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
    revoke_api_key(db, key)
