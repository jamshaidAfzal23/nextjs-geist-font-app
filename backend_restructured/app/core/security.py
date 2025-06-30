"""
Security utilities for Smart CRM SaaS application.
This module contains authentication, authorization, and security-related functions.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

from datetime import datetime, timedelta

from .config import settings
from ..models import User
from ..core.database import get_database_session

# Password hashing context
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password (str): Plain text password to hash
        
    Returns:
        str: Hashed password
        
    Example:
        hashed = hash_password("user_password")
    """
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        is_valid = verify_password("user_password", stored_hash)
    """
    return password_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time
        
    Returns:
        str: JWT access token
        
    Example:
        token = create_access_token({"sub": user.email})
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
        
    Example:
        payload = verify_token(access_token)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def check_user_permissions(user_role: str, required_permission: str) -> bool:
    """
    Check if a user has the required permission based on their role.
    
    Args:
        user_role (str): User's role (e.g., 'admin', 'manager', 'user')
        required_permission (str): Required permission to check
        
    Returns:
        bool: True if user has permission, False otherwise
        
    Example:
        has_access = check_user_permissions(user.role, "delete_client")
    """
    # Define role-based permissions
    role_permissions = {
        "admin": ["create", "read", "update", "delete", "manage_users"],
        "manager": ["create", "read", "update", "delete"],
        "user": ["create", "read", "update"],
        "viewer": ["read"]
    }
    
    user_permissions = role_permissions.get(user_role, [])
    return required_permission in user_permissions

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_database_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
