"""
Security utilities for Smart CRM SaaS application.
This module contains authentication, authorization, and security-related functions.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..auth.auth import verify_token
from ..models.user_model import User
from ..core.database import get_database_session

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
