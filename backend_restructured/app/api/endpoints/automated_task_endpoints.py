"""
API endpoints for managing automated tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.automated_task_model import AutomatedTask
from ...schemas.automated_task_schemas import (
    AutomatedTaskCreate, AutomatedTaskUpdate, AutomatedTaskResponse
)

router = APIRouter()


@router.post("/", response_model=AutomatedTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_automated_task(
    task_data: AutomatedTaskCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new automated task.
    """
    db_task = AutomatedTask(
        **task_data.dict(),
        created_by_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/", response_model=List[AutomatedTaskResponse])
async def get_automated_tasks(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    task_type: Optional[str] = Query(None),
    is_completed: Optional[bool] = Query(None),
):
    """
    Get a list of automated tasks.
    """
    query = db.query(AutomatedTask).filter(AutomatedTask.created_by_id == current_user.id)

    if task_type:
        query = query.filter(AutomatedTask.task_type == task_type)
    if is_completed is not None:
        query = query.filter(AutomatedTask.is_completed == is_completed)

    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.put("/{task_id}", response_model=AutomatedTaskResponse)
async def update_automated_task(
    task_id: int,
    task_data: AutomatedTaskUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update an automated task.
    """
    task = db.query(AutomatedTask).filter(AutomatedTask.id == task_id, AutomatedTask.created_by_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    for field, value in task_data.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    if task_data.is_completed and not task.completed_at:
        task.completed_at = datetime.now()
    elif not task_data.is_completed and task.completed_at:
        task.completed_at = None

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automated_task(
    task_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an automated task.
    """
    task = db.query(AutomatedTask).filter(AutomatedTask.id == task_id, AutomatedTask.created_by_id == current_user.id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()
