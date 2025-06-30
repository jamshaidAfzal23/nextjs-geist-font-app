"""
Role-Based Access Control (RBAC) for the Smart CRM SaaS application.
"""

from fastapi import Depends, HTTPException, status
from .security import get_current_user
from ..models import User

# Define roles and their permissions
# In a real application, this would be more sophisticated, perhaps stored in a database
ROLES = {
    "Admin": ["*"],
    "Bidder": ["clients:read", "projects:read", "projects:create"],
    "Developer": ["projects:read", "projects:update"],
    "Finance": ["payments:read", "expenses:read", "invoices:read", "financial:read"],
}

def check_permissions(required_permissions: list[str]):
    """
    Dependency to check if a user has the required permissions.
    """
    async def _check_permissions(current_user: User = Depends(get_current_user)):
        user_permissions = ROLES.get(current_user.role, [])
        if "*" in user_permissions:
            return current_user
        
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action.",
                )
        return current_user
    return _check_permissions
