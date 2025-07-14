"""
User API endpoints for Smart CRM SaaS application.
This module defines all user-related API routes including user management and profile operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_database_session
from ...core.security import get_current_user
from ...auth.auth import hash_password, verify_password
from ...models.user_model import User
from ...schemas.user_schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, PasswordChange, UserCreateBulk
)
from .user_preference_endpoints import router as user_preferences_router

# Create router for user endpoints with proper prefix
router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user account (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users."
        )
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = hash_password(user_data.password)
    db_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/bulk", response_model=List[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_multiple_users(
    users_data: UserCreateBulk,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple user accounts in a single request.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users in bulk."
        )

    created_users = []
    for user_data in users_data.users:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user_data.email} already registered"
            )
        
        hashed_password = hash_password(user_data.password)
        
        db_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role
        )
        
        db.add(db_user)
        created_users.append(db_user)
    
    db.commit()
    for user in created_users:
        db.refresh(user)
    
    return created_users


@router.put("/bulk", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def update_multiple_users(
    users_data: List[UserUpdate],
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update multiple user accounts in a single request.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update users in bulk."
        )

    updated_users = []
    for user_data in users_data:
        user = db.query(User).filter(User.id == user_data.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_data.id} not found"
            )
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        updated_users.append(user)
    
    db.commit()
    for user in updated_users:
        db.refresh(user)
    
    return updated_users


@router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT)
async def delete_multiple_users(
    user_ids: List[int],
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete multiple user accounts in a single request.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users in bulk."
        )

    for user_id in user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        db.delete(user)
    
    db.commit()


from ..dependencies import get_pagination_params, get_sorting_params

@router.get("/", response_model=UserListResponse)
async def get_users(
    pagination: dict = Depends(get_pagination_params),
    sorting: dict = Depends(get_sorting_params),
    search: Optional[str] = Query(None, description="Search term for name or email"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response (e.g., 'id,full_name,email')"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a paginated list of users with optional filtering, sorting, and field selection.
    """
    query = db.query(User)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_filter)) |
            (User.email.ilike(search_filter))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Apply sorting
    sort_by = sorting["sort_by"]
    sort_order = sorting["sort_order"]
    if sort_by:
        if hasattr(User, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(User, sort_by).desc())
            else:
                query = query.order_by(getattr(User, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    skip = pagination["skip"]
    limit = pagination["limit"]
    users = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        # Filter the dictionary representation of each user
        processed_users = []
        for user in users:
            user_dict = user.__dict__.copy()
            filtered_user = {k: v for k, v in user_dict.items() if k in selected_fields}
            processed_users.append(filtered_user)
        users = processed_users
    else:
        # If no fields are specified, return the full UserResponse schema
        users = [UserResponse.from_orm(user) for user in users]
    
    # Calculate pagination values directly
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    # Return the response directly
    return {
        "items": users,
        "total": total,
        "page": page,
        "size": limit,
        "pages": pages
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current authenticated user's profile information.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Update the current authenticated user's profile information.
    """
    for field, value in user_data.dict(exclude_unset=True).items():
        if field != "id":  # Don't allow updating ID
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_current_user_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Change the current authenticated user's password.
    """
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific user by ID.
    """
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    for field, value in user_data.dict(exclude_unset=True).items():
        if field != "id":  # Don't allow updating ID
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific user by ID.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete users"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()

router.include_router(user_preferences_router, prefix="/me/preferences", tags=["User Preferences"])
