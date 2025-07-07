from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.schemas.user_schema import UserPreferences
from app.models.user_model import User
from app.models.user_preference_model import UserPreference
from app.core.database import get_database_session

router = APIRouter()

@router.get("/users/me/preferences", response_model=UserPreferences)
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    return preferences

@router.put("/users/me/preferences", response_model=UserPreferences)
def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    db_preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not db_preferences:
        db_preferences = UserPreference(user_id=current_user.id)
        db.add(db_preferences)
    
    for field, value in preferences.dict().items():
        setattr(db_preferences, field, value)
    
    db.commit()
    db.refresh(db_preferences)
    
    return db_preferences