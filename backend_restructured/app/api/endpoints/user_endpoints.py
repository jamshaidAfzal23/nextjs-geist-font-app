"""
User API endpoints for Smart CRM SaaS application.
This module defines all user-related API routes including authentication,
user management, and profile operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_database_session
from ...core.security import hash_password, verify_password, create_access_token, check_user_permissions, get_current_user
from ...models import User
from ...schemas import (
    UserCreate, UserUpdate, UserResponse, UserLogin, UserToken,
    UserListResponse, PasswordChange
)

# Create router for user endpoints with proper prefix
router = APIRouter(prefix="/users", tags=["users"])



@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)

async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_database_session)
):
    """
    Create a new user account.
    
    Args:
        user_data (UserCreate): User registration data
        db (Session): Database session
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user with email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
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

@router.post("/login", response_model=UserToken, include_in_schema=False)

async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_database_session)
):
    """
    Authenticate user and return access token.
    
    Args:
        login_data (UserLogin): User login credentials
        db (Session): Database session
        
    Returns:
        UserToken: Access token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for name or email"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a paginated list of users with optional filtering.
    
    Args:
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return
        search (str, optional): Search term for name or email
        role (str, optional): Filter by user role
        is_active (bool, optional): Filter by active status
        db (Session): Database session
        
    Returns:
        UserListResponse: Paginated list of users
    """
    # Build query with filters
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
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    return {
        "users": users,
        "total": total,
        "page": (skip // limit) + 1,
        "per_page": limit
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user

@router.get("/{user_id}", response_model=UserResponse)


async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user
