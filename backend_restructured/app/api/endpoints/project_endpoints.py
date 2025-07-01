"""
Project API endpoints for Smart CRM SaaS application.
This module defines all project-related API routes including project management,
project tracking, and project analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from ...core.database import get_database_session
from ...core.rbac import check_permissions
from ...models import Project, Client, User, Payment, Expense
from ...models.project_model import ProjectStatus, ProjectPriority
from ...schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectSummary, ProjectSearchFilters, ProjectStats, ProjectCreateBulk, ProjectUpdateBulk, ProjectDeleteBulk
)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["projects:create"]))])
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_database_session)
):
    """
    Create a new project.
    """
    # Verify client exists
    client = db.query(Client).filter(Client.id == project_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Verify developer exists (if provided)
    if project_data.developer_id:
        developer = db.query(User).filter(User.id == project_data.developer_id).first()
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer not found"
            )
    
    # Create new project
    db_project = Project(**project_data.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project


@router.post("/bulk", response_model=List[ProjectResponse], status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["projects:create"]))])
async def create_multiple_projects(
    projects_data: ProjectCreateBulk,
    db: Session = Depends(get_database_session)
):
    """
    Create multiple project records in a single request.
    """
    created_projects = []
    for project_data in projects_data.projects:
        # Verify client exists
        client = db.query(Client).filter(Client.id == project_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {project_data.client_id} not found for project {project_data.title}"
            )
        
        # Verify developer exists (if provided)
        if project_data.developer_id:
            developer = db.query(User).filter(User.id == project_data.developer_id).first()
            if not developer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Developer with ID {project_data.developer_id} not found for project {project_data.title}"
                )
        
        db_project = Project(**project_data.dict())
        db.add(db_project)
        created_projects.append(db_project)
    
    db.commit()
    for project in created_projects:
        db.refresh(project)
    
    return created_projects


@router.put("/bulk", response_model=List[ProjectResponse], status_code=status.HTTP_200_OK, dependencies=[Depends(check_permissions(["projects:update"]))])
async def update_multiple_projects(
    projects_data: ProjectUpdateBulk,
    db: Session = Depends(get_database_session)
):
    """
    Update multiple project records in a single request.
    """
    updated_projects = []
    for project_data in projects_data.projects:
        project = db.query(Project).filter(Project.id == project_data.id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_data.id} not found"
            )
        
        # Verify developer exists (if being updated)
        if project_data.developer_id:
            developer = db.query(User).filter(User.id == project_data.developer_id).first()
            if not developer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Developer with ID {project_data.developer_id} not found for project {project.title}"
                )
        
        # Validate status transition
        if project_data.status and project_data.status != project.status:
            if project_data.status not in VALID_STATUS_TRANSITIONS.get(project.status, []):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status transition from {project.status} to {project_data.status}"
                )

        for field, value in project_data.dict(exclude_unset=True).items():
            setattr(project, field, value)
        
        # Set actual_end_date if status is completed
        if project_data.status == ProjectStatus.COMPLETED and not project.actual_end_date:
            project.actual_end_date = datetime.now()
        
        updated_projects.append(project)
    
    db.commit()
    for project in updated_projects:
        db.refresh(project)
    
    return updated_projects


@router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(check_permissions(["projects:delete"]))])
async def delete_multiple_projects(
    project_ids_data: ProjectDeleteBulk,
    db: Session = Depends(get_database_session)
):
    """
    Delete multiple project records in a single request.
    """
    for project_id in project_ids_data.project_ids:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        db.delete(project)
    
    db.commit()

@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for project title"),
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    priority: Optional[ProjectPriority] = Query(None, description="Filter by project priority"),
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    developer_id: Optional[int] = Query(None, description="Filter by developer ID"),
    is_overdue: Optional[bool] = Query(None, description="Filter overdue projects"),
    sort_by: Optional[str] = Query(None, description="Field to sort by (e.g., 'title', 'start_date', 'end_date')"),
    sort_order: Optional[str] = Query("asc", description="Sort order ('asc' or 'desc')"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response (e.g., 'id,title,status')"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a paginated list of projects with optional filtering and sorting.
    """
    # Build query with filters
    query = db.query(Project)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(Project.title.ilike(search_filter))
    
    if status:
        query = query.filter(Project.status == status)
    
    if priority:
        query = query.filter(Project.priority == priority)
    
    if client_id:
        query = query.filter(Project.client_id == client_id)
    
    if developer_id:
        query = query.filter(Project.developer_id == developer_id)
    
    if is_overdue:
        current_time = datetime.now()
        query = query.filter(
            and_(
                Project.end_date < current_time,
                Project.status.notin_([ProjectStatus.COMPLETED, ProjectStatus.CANCELLED])
            )
        )
    
    # Apply sorting
    if sort_by:
        if hasattr(Project, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(Project, sort_by).desc())
            else:
                query = query.order_by(getattr(Project, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a specific project by ID.
    
    Args:
        project_id (int): Project ID to retrieve
        db (Session): Database session
        
    Returns:
        ProjectResponse: Project information with computed fields
        
    Raises:
        HTTPException: If project not found
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Create enhanced response with computed fields
    project_dict = project.__dict__.copy()
    project_dict['is_overdue'] = project.is_overdue
    project_dict['total_expenses'] = project.total_expenses
    project_dict['total_payments'] = project.total_payments
    project_dict['profit_margin'] = project.profit_margin
    
    # Add related data
    if project.client:
        project_dict['client_name'] = project.client.company_name
    if project.developer:
        project_dict['developer_name'] = project.developer.full_name
    
    return project_dict

@router.put("/{project_id}", response_model=ProjectResponse, dependencies=[Depends(check_permissions(["projects:update"]))])
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_database_session)
):
    """
    Update project information.
    
    Args:
        project_id (int): Project ID to update
        project_data (ProjectUpdate): Updated project data
        db (Session): Database session
        
    Returns:
        ProjectResponse: Updated project information
        
    Raises:
        HTTPException: If project not found or invalid developer ID
    """
    # Find project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Verify developer exists (if being updated)
    if project_data.developer_id:
        developer = db.query(User).filter(User.id == project_data.developer_id).first()
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer not found"
            )
    
    # Update project fields
    update_data = project_data.dict(exclude_unset=True)

    # Validate status transition
    if "status" in update_data and update_data["status"] != project.status:
        if update_data["status"] not in VALID_STATUS_TRANSITIONS.get(project.status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {project.status} to {update_data['status']}"
            )

    for field, value in update_data.items():
        setattr(project, field, value)
    
    # Set actual_end_date if status is completed
    if project_data.status == ProjectStatus.COMPLETED and not project.actual_end_date:
        project.actual_end_date = datetime.now()
    
    db.commit()
    db.refresh(project)
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(check_permissions(["projects:delete"]))])
async def delete_project(
    project_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Delete a project.
    
    Args:
        project_id (int): Project ID to delete
        db (Session): Database session
        
    Raises:
        HTTPException: If project not found
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()

@router.get("/summary/stats", response_model=ProjectStats)
async def get_project_stats(
    db: Session = Depends(get_database_session)
):
    """
    Get project statistics and analytics.
    
    Args:
        db (Session): Database session
        
    Returns:
        ProjectStats: Aggregated project statistics
    """
    # Get total projects
    total_projects = db.query(func.count(Project.id)).scalar()
    
    # Get projects by status
    projects_by_status = db.query(
        Project.status,
        func.count(Project.id)
    ).group_by(Project.status).all()
    
    # Get projects by priority
    projects_by_priority = db.query(
        Project.priority,
        func.count(Project.id)
    ).group_by(Project.priority).all()
    
    # Get overdue projects
    current_time = datetime.now()
    overdue_projects = db.query(func.count(Project.id))\
        .filter(
            and_(
                Project.end_date < current_time,
                Project.status.notin_([ProjectStatus.COMPLETED, ProjectStatus.CANCELLED])
            )
        ).scalar()
    
    # Get total budget
    total_budget = db.query(func.sum(Project.budget)).scalar() or 0.0
    
    # Calculate average project duration
    completed_projects = db.query(Project)\
        .filter(
            and_(
                Project.status == ProjectStatus.COMPLETED,
                Project.start_date.isnot(None),
                Project.actual_end_date.isnot(None)
            )
        ).all()
    
    avg_duration = None
    if completed_projects:
        total_duration = sum(
            (p.actual_end_date - p.start_date).days 
            for p in completed_projects
        )
        avg_duration = total_duration / len(completed_projects)
    
    # Calculate completion rate
    completed_count = db.query(func.count(Project.id))\
        .filter(Project.status == ProjectStatus.COMPLETED)\
        .scalar()
    completion_rate = (completed_count / total_projects * 100) if total_projects > 0 else 0
    
    return {
        "total_projects": total_projects,
        "projects_by_status": dict(projects_by_status),
        "projects_by_priority": dict(projects_by_priority),
        "overdue_projects": overdue_projects,
        "total_budget": total_budget,
        "average_project_duration": avg_duration,
        "completion_rate": completion_rate
    }

@router.get("/client/{client_id}/projects", response_model=List[ProjectSummary])
async def get_client_projects(
    client_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Get all projects for a specific client.
    
    Args:
        client_id (int): Client ID
        db (Session): Database session
        
    Returns:
        List[ProjectSummary]: List of projects for the client
        
    Raises:
        HTTPException: If client not found
    """
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Get client projects
    projects = db.query(Project)\
        .filter(Project.client_id == client_id)\
        .all()
    
    # Create project summaries
    project_summaries = []
    for project in projects:
        summary = {
            "id": project.id,
            "title": project.title,
            "status": project.status,
            "priority": project.priority,
            "client_name": client.company_name,
            "budget": project.budget,
            "progress_percentage": None  # This would be calculated based on milestones
        }
        project_summaries.append(summary)
    
    return project_summaries

@router.post("/{project_id}/complete", response_model=ProjectResponse)
async def complete_project(
    project_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Mark a project as completed.
    
    Args:
        project_id (int): Project ID to complete
        db (Session): Database session
        
    Returns:
        ProjectResponse: Updated project information
        
    Raises:
        HTTPException: If project not found
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project.status = ProjectStatus.COMPLETED
    project.actual_end_date = datetime.now()
    
    db.commit()
    db.refresh(project)
    
    return project
