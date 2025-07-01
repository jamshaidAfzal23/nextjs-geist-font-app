"""
API endpoints for database backup management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from ...core.security import get_current_user
from ...models.user_model import User
from ...services.backup_service import create_database_backup

router = APIRouter()


@router.post("/backup", status_code=status.HTTP_200_OK)
async def trigger_database_backup(
    current_user: User = Depends(get_current_user)
):
    """
    Trigger a manual database backup.
    (Requires admin privileges)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can trigger backups."
        )
    try:
        backup_path = create_database_backup()
        return {"message": "Database backup created successfully", "path": backup_path}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create database backup: {e}"
        )
