"""
API endpoints for managing report templates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.report_template_model import ReportTemplate
from ...schemas.report_template_schemas import (
    ReportTemplateCreate, ReportTemplateUpdate, ReportTemplateResponse
)

router = APIRouter()


@router.post("/", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_report_template(
    template_data: ReportTemplateCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new report template.
    """
    db_template = ReportTemplate(
        **template_data.dict(),
        user_id=current_user.id
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/", response_model=List[ReportTemplateResponse])
async def get_report_templates(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get a list of report templates for the current user.
    """
    templates = db.query(ReportTemplate).filter(ReportTemplate.user_id == current_user.id).offset(skip).limit(limit).all()
    return templates


@router.put("/{template_id}", response_model=ReportTemplateResponse)
async def update_report_template(
    template_id: int,
    template_data: ReportTemplateUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific report template.
    """
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id, ReportTemplate.user_id == current_user.id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )

    for field, value in template_data.dict(exclude_unset=True).items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report_template(
    template_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific report template.
    """
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id, ReportTemplate.user_id == current_user.id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report template not found"
        )

    db.delete(template)
    db.commit()
