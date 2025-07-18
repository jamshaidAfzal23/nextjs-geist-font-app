"""
Role-Based Access Control (RBAC) for the Smart CRM SaaS application.
This module provides a flexible RBAC system with role hierarchy, permission decorators,
and middleware for protecting API endpoints.
"""

from functools import wraps
from typing import Callable, Dict, List, Set 

from fastapi import Depends, HTTPException, Request, status

from ..core.security import get_current_user
from ..models.user_model import User

# Define role hierarchy. Roles inherit permissions from parent roles.
# For example, a 'manager' inherits all 'user' permissions.
ROLE_HIERARCHY: Dict[str, List[str]] = {
    "admin": ["manager"],
    "manager": ["user"],
    "user": ["viewer"],
    "viewer": [],
}

# Define permissions for each role.
# Permissions are additive and inherited from parent roles.
PERMISSIONS: Dict[str, List[str]] = {
    "admin": [
        "users:create", "users:delete", "roles:manage", "system:config"
    ],
    "manager": [
        "clients:create", "clients:update", "clients:delete",
        "projects:create", "projects:update", "projects:delete",
        "reports:generate"
    ],
    "user": [
        "clients:read", "projects:read", "tasks:create", "tasks:update"
    ],
    "viewer": [
        "dashboard:read"
    ],
}

def get_role_permissions(role: str) -> Set[str]:
    """
    Get all permissions for a given role, including inherited permissions.
    """
    permissions = set(PERMISSIONS.get(role, []))
    for parent_role in ROLE_HIERARCHY.get(role, []):
        permissions.update(get_role_permissions(parent_role))
    return permissions


def require_permission(required_permission: str) -> Callable:
    """
    Decorator to protect an endpoint, requiring a specific permission.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user: User = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            user_permissions = get_role_permissions(current_user.role)
            if required_permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action.",
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def rbac_middleware(request: Request, call_next: Callable):
    """
    RBAC middleware to protect routes based on user roles and permissions.
    This is an example of how you might implement route-based protection.
    In a real application, you would likely have more sophisticated logic here.
    """
    # In a real implementation, you would look up the required permission for the requested route.
    # For example, you could have a mapping of routes to required permissions.
    # For now, we'll just allow all authenticated users to proceed.
    # The `require_permission` decorator will handle endpoint-specific protection.

    response = await call_next(request)
    return response


def check_permissions(user: User, required_permission: str) -> bool:
    """
    Check if a user has the required permission.
    
    Args:
        user: The user object to check permissions for
        required_permission: The permission string to check (e.g. 'clients:read')
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not user:
        return False
    user_permissions = get_role_permissions(user.role)
    return required_permission in user_permissions


def require_permissions(required_permission: str):
    """
    Dependency function to check if current user has required permission.
    
    Args:
        required_permission: The permission string to check (e.g. 'clients:read')
        
    Returns:
        Dependency function for FastAPI
    """
    def permission_dependency(current_user: User = Depends(get_current_user)):
        if not check_permissions(current_user, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )
        return current_user
    return permission_dependency
