"""User-related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.security import get_current_user, hash_password
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.models.user_model import User
from app.core.database import get_database_session
from app.utils.pagination import paginate_results

router = APIRouter()

@router.get("/users", response_model=dict)
async def get_users(
    db: Session = Depends(get_database),
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None
):
    """Get all users with pagination and optional search."""
    query = db.query(User)
    
    if search:
        query = query.filter(
            User.email.ilike(f"%{search}%") |
            User.full_name.ilike(f"%{search}%")
        )
    
    users = query.all()
    return paginate_results([user.to_dict() for user in users], page, size)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: Session = Depends(get_database)):
    """Get a specific user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_database)):
    """Create a new user."""
    try:
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Update a user."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update failed due to constraint violation"
        )

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Delete a user."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()

@router.get("/users/{user_id}/preferences", response_model=UserPreferences)
async def get_user_preferences(
    user_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get user preferences."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.preferences

@router.put("/users/{user_id}/preferences", response_model=UserPreferences)
async def update_user_preferences(
    user_id: int,
    preferences: UserPreferences,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Update user preferences."""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.preferences = preferences.dict()
    db.commit()
    db.refresh(user)
    return user.preferences