"""
API endpoints for managing scheduled reports.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...models.scheduled_report_model import ScheduledReport
from ...schemas.scheduled_report_schemas import (
    ScheduledReportCreate, ScheduledReportUpdate, ScheduledReportResponse
)

router = APIRouter()


@router.post("/", response_model=ScheduledReportResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_report(
    report_data: ScheduledReportCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new scheduled report.
    """
    db_report = ScheduledReport(
        **report_data.dict(),
        user_id=current_user.id
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/", response_model=List[ScheduledReportResponse])
async def get_scheduled_reports(
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get a list of scheduled reports for the current user.
    """
    reports = db.query(ScheduledReport).filter(ScheduledReport.user_id == current_user.id).offset(skip).limit(limit).all()
    return reports


@router.put("/{report_id}", response_model=ScheduledReportResponse)
async def update_scheduled_report(
    report_id: int,
    report_data: ScheduledReportUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific scheduled report.
    """
    report = db.query(ScheduledReport).filter(ScheduledReport.id == report_id, ScheduledReport.user_id == current_user.id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found"
        )

    for field, value in report_data.dict(exclude_unset=True).items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_report(
    report_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific scheduled report.
    """
    report = db.query(ScheduledReport).filter(ScheduledReport.id == report_id, ScheduledReport.user_id == current_user.id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled report not found"
        )

    db.delete(report)
    db.commit()
