"""
Client API endpoints for Smart CRM SaaS application.
This module defines all client-related API routes including client management,
client information retrieval, and client statistics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from ...core.database import get_database_session
from ...core.rbac import check_permissions
from ...models import Client, Project, Payment
from ...schemas import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListResponse,
    ClientSummary, ClientSearchFilters, ClientStats
)

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(check_permissions(["clients:create"]))])
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_database_session)
):
    """
    Create a new client.
    
    Args:
        client_data (ClientCreate): Client creation data
        db (Session): Database session
        
    Returns:
        ClientResponse: Created client information
        
    Raises:
        HTTPException: If client with same email already exists
    """
    # Check if client with email already exists
    existing_client = db.query(Client).filter(Client.email == client_data.email).first()
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this email already exists"
        )
    
    # Create new client
    db_client = Client(**client_data.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return db_client

@router.get("/", response_model=ClientListResponse)
async def get_clients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search term for company or contact name"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    platform: Optional[str] = Query(None, description="Filter by platform preference"),
    assigned_user_id: Optional[int] = Query(None, description="Filter by assigned user"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a paginated list of clients with optional filtering.
    
    Args:
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return
        search (str, optional): Search term for company or contact name
        industry (str, optional): Filter by industry
        platform (str, optional): Filter by platform preference
        assigned_user_id (int, optional): Filter by assigned user
        db (Session): Database session
        
    Returns:
        ClientListResponse: Paginated list of clients
    """
    # Build query with filters
    query = db.query(Client)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Client.company_name.ilike(search_filter)) |
            (Client.contact_person_name.ilike(search_filter))
        )
    
    if industry:
        query = query.filter(Client.industry == industry)
    
    if platform:
        query = query.filter(Client.platform_preference == platform)
    
    if assigned_user_id:
        query = query.filter(Client.assigned_user_id == assigned_user_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    clients = query.offset(skip).limit(limit).all()
    
    return {
        "clients": clients,
        "total": total,
        "page": (skip // limit) + 1,
        "per_page": limit
    }

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a specific client by ID.
    
    Args:
        client_id (int): Client ID to retrieve
        db (Session): Database session
        
    Returns:
        ClientResponse: Client information
        
    Raises:
        HTTPException: If client not found
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client

@router.put("/{client_id}", response_model=ClientResponse, dependencies=[Depends(check_permissions(["clients:update"]))])
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_database_session)
):
    """
    Update client information.
    
    Args:
        client_id (int): Client ID to update
        client_data (ClientUpdate): Updated client data
        db (Session): Database session
        
    Returns:
        ClientResponse: Updated client information
        
    Raises:
        HTTPException: If client not found or email already exists
    """
    # Find client
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Check if email is being updated and already exists
    if client_data.email and client_data.email != client.email:
        existing_client = db.query(Client).filter(Client.email == client_data.email).first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered to another client"
            )
    
    # Update client fields
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(check_permissions(["clients:delete"]))])
async def delete_client(
    client_id: int,
    db: Session = Depends(get_database_session)
):
    """
    Delete a client.
    
    Args:
        client_id (int): Client ID to delete
        db (Session): Database session
        
    Raises:
        HTTPException: If client not found
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db.delete(client)
    db.commit()

@router.get("/summary/stats", response_model=ClientStats)
async def get_client_stats(
    db: Session = Depends(get_database_session)
):
    """
    Get client statistics and analytics.
    
    Args:
        db (Session): Database session
        
    Returns:
        ClientStats: Aggregated client statistics
    """
    # Get total clients
    total_clients = db.query(func.count(Client.id)).scalar()
    
    # Get clients with active projects
    active_clients = db.query(func.count(Client.id.distinct()))\
        .join(Project)\
        .filter(Project.status.in_(['active', 'in_progress']))\
        .scalar()
    
    # Get clients by industry
    clients_by_industry = db.query(
        Client.industry,
        func.count(Client.id)
    ).group_by(Client.industry).all()
    
    # Get clients by assigned user
    clients_by_user = db.query(
        Client.assigned_user_id,
        func.count(Client.id)
    ).group_by(Client.assigned_user_id).all()
    
    # Calculate average project value
    avg_project_value = db.query(func.avg(Project.budget))\
        .join(Client)\
        .scalar() or 0.0
    
    # Get top clients by project value
    top_clients = db.query(
        Client.id,
        Client.company_name,
        func.sum(Project.budget).label('total_value')
    ).join(Project)\
    .group_by(Client.id)\
    .order_by(func.sum(Project.budget).desc())\
    .limit(5)\
    .all()
    
    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "clients_by_industry": dict(clients_by_industry),
        "clients_by_user": dict(clients_by_user),
        "average_project_value": avg_project_value,
        "top_clients_by_value": [
            {
                "id": c.id,
                "name": c.company_name,
                "total_value": float(c.total_value)
            }
            for c in top_clients
        ]
    }

@router.get("/search/advanced", response_model=ClientListResponse)
async def search_clients(
    filters: ClientSearchFilters = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_database_session)
):
    """
    Advanced search for clients with multiple filters.
    
    Args:
        filters (ClientSearchFilters): Search and filter parameters
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        db (Session): Database session
        
    Returns:
        ClientListResponse: Filtered and paginated list of clients
    """
    query = db.query(Client)
    
    if filters.search_term:
        search_filter = f"%{filters.search_term}%"
        query = query.filter(
            (Client.company_name.ilike(search_filter)) |
            (Client.contact_person_name.ilike(search_filter))
        )
    
    if filters.industry:
        query = query.filter(Client.industry == filters.industry)
    
    if filters.assigned_user_id:
        query = query.filter(Client.assigned_user_id == filters.assigned_user_id)
    
    if filters.platform_preference:
        query = query.filter(Client.platform_preference == filters.platform_preference)
    
    if filters.has_active_projects:
        query = query.join(Project)\
            .filter(Project.status.in_(['active', 'in_progress']))\
            .group_by(Client.id)
    
    if filters.created_after:
        query = query.filter(Client.created_at >= filters.created_after)
    
    if filters.created_before:
        query = query.filter(Client.created_at <= filters.created_before)
    
    total = query.count()
    clients = query.offset(skip).limit(limit).all()
    
    return {
        "clients": clients,
        "total": total,
        "page": (skip // limit) + 1,
        "per_page": limit
    }
