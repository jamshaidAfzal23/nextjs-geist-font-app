"""User-related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import get_current_user, hash_password
from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse, UserPreferences
from app.models.user_model import User
from app.models.user_preference_model import UserPreference
from app.core.database import get_database_session
from app.utils.pagination import paginate_results

router = APIRouter()

@router.get("/users", response_model=dict)
async def get_users(
    db: Session = Depends(get_database_session),
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None
):
    """Get all users with pagination and search."""
    query = db.query(User)
    
    if search:
        search = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search)) |
            (User.full_name.ilike(search))
        )
    
    return paginate_results(query, page, size)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: Session = Depends(get_database_session)):
    """Get a specific user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new user."""
    # Only admin can create users
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create users"
        )
    
    # Check if user with email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create new user
        hashed_password = hash_password(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role,
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        raise

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Update user information."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user fields
    for field, value in user_update.dict(exclude_unset=True).items():
        if field == "password" and value is not None:
            setattr(db_user, "hashed_password", hash_password(value))
        elif value is not None:
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user
        raise HTTPException(status_code=403, detail="Not authorized")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for field, value in update_data.items():
        setattr(db_user, field, value)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        if "unique constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        raise

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a user."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.delete(db_user)
        db.commit()
    except Exception:
        db.rollback()
        raise

@router.get("/users/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Get current user preferences."""
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not preferences:
        # Create default preferences if they don't exist
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return preferences

@router.put("/users/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """Update current user preferences."""
    db_preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not db_preferences:
        db_preferences = UserPreference(user_id=current_user.id)
        db.add(db_preferences)
    
    # Update preference fields
    for field, value in preferences.dict().items():
        setattr(db_preferences, field, value)
    
    db.commit()
    db.refresh(db_preferences)
    return db_preferences
    db.refresh(user)
    return user.preferences