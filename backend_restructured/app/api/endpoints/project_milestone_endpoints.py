"""
API endpoints for managing project milestones.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.project_model import Project
from ...models.project_milestone_model import ProjectMilestone
from ...schemas.project_milestone_schemas import (
    ProjectMilestoneCreate, ProjectMilestoneUpdate, ProjectMilestoneResponse
)

router = APIRouter()


@router.post("/{project_id}/milestones", response_model=ProjectMilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_project_milestone(
    project_id: int,
    milestone_data: ProjectMilestoneCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new milestone for a specific project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_milestone = ProjectMilestone(
        project_id=project_id,
        title=milestone_data.title,
        description=milestone_data.description,
        due_date=milestone_data.due_date
    )
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone


@router.get("/{project_id}/milestones", response_model=List[ProjectMilestoneResponse])
async def get_project_milestones(
    project_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get all milestones for a specific project.
    """
    milestones = db.query(ProjectMilestone).filter(ProjectMilestone.project_id == project_id).offset(skip).limit(limit).all()
    return milestones


@router.put("/milestones/{milestone_id}", response_model=ProjectMilestoneResponse)
async def update_project_milestone(
    milestone_id: int,
    milestone_data: ProjectMilestoneUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific project milestone.
    """
    milestone = db.query(ProjectMilestone).filter(ProjectMilestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    for field, value in milestone_data.dict(exclude_unset=True).items():
        setattr(milestone, field, value)
    
    if milestone_data.is_completed and not milestone.completed_at:
        milestone.completed_at = datetime.now()
    elif not milestone_data.is_completed and milestone.completed_at:
        milestone.completed_at = None

    db.commit()
    db.refresh(milestone)
    return milestone


@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_milestone(
    milestone_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific project milestone.
    """
    milestone = db.query(ProjectMilestone).filter(ProjectMilestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    db.delete(milestone)
    db.commit()
