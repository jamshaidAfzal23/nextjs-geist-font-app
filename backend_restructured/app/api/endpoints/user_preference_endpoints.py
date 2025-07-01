"""
API endpoints for managing user preferences.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.user_preference_model import UserPreference
from ...schemas.user_preference_schemas import (
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse
)

router = APIRouter()


@router.get("/", response_model=UserPreferenceResponse)
async def get_user_preferences(db: Session = Depends(get_database_session), current_user: User = Depends(get_current_user)):
    """Get the current user's preferences."""
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not preferences:
        # If preferences don't exist, create them with default values
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    return preferences


@router.put("/", response_model=UserPreferenceResponse)
async def update_user_preferences(
    preference_data: UserPreferenceUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Update the current user's preferences."""
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )

    for field, value in preference_data.dict(exclude_unset=True).items():
        setattr(preferences, field, value)
    
    db.commit()
    db.refresh(preferences)
    return preferences
