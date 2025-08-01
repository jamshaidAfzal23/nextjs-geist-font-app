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
from ...core.security import get_current_user
from ...models.client_model import Client
from ...models.project_model import Project
from ...models.financial_model import Payment
from ...models.user_model import User
from ...schemas.client_schemas import (
    ClientCreate, ClientUpdate, ClientResponse, ClientListResponse,
    ClientSummary, ClientSearchFilters, ClientStats, ClientCreateBulk, ClientUpdateBulk, ClientDeleteBulk
)

router = APIRouter(tags=["clients"])

@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new client.
    """
    # Check if client with email already exists
    existing_client = db.query(Client).filter(Client.email == client_data.email).first()
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this email already exists"
        )
    
    # Create new client
    client_dict = client_data.model_dump()
    # Map 'notes' to 'general_notes' if present
    if 'notes' in client_dict:
        client_dict['general_notes'] = client_dict.pop('notes')
    
    db_client = Client(**client_dict)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    return db_client


@router.post("/bulk", response_model=List[ClientResponse], status_code=status.HTTP_201_CREATED)
async def create_multiple_clients(
    clients_data: ClientCreateBulk,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple client records in a single request.
    """
    created_clients = []
    for client_data in clients_data.clients:
        existing_client = db.query(Client).filter(Client.email == client_data.email).first()
        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Client with email {client_data.email} already exists"
            )
        client_dict = client_data.model_dump()
        # Map 'notes' to 'general_notes' if present
        if 'notes' in client_dict:
            client_dict['general_notes'] = client_dict.pop('notes')
        
        db_client = Client(**client_dict)
        db.add(db_client)
        created_clients.append(db_client)
    
    db.commit()
    for client in created_clients:
        db.refresh(client)
    
    return created_clients


@router.put("/bulk", response_model=List[ClientResponse], status_code=status.HTTP_200_OK)
async def update_multiple_clients(
    clients_data: ClientUpdateBulk,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update multiple client records in a single request.
    """
    updated_clients = []
    for client_data in clients_data.clients:
        client = db.query(Client).filter(Client.id == client_data.id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_data.id} not found"
            )
        
        if client_data.email and client_data.email != client.email:
            existing_client = db.query(Client).filter(Client.email == client_data.email).first()
            if existing_client:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {client_data.email} already registered to another client"
                )
        
        client_dict = client_data.model_dump(exclude_unset=True)
        # Map 'notes' to 'general_notes' if present
        if 'notes' in client_dict:
            client_dict['general_notes'] = client_dict.pop('notes')
        
        for field, value in client_dict.items():
            setattr(client, field, value)
        updated_clients.append(client)
    
    db.commit()
    for client in updated_clients:
        db.refresh(client)
    
    return updated_clients


@router.delete("/bulk", status_code=status.HTTP_204_NO_CONTENT)
async def delete_multiple_clients(
    client_ids_data: ClientDeleteBulk,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete multiple client records in a single request.
    """
    for client_id in client_ids_data.client_ids:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found"
            )
        db.delete(client)
    
    db.commit()

from ..dependencies import get_pagination_params, get_sorting_params

@router.get("/", response_model=ClientListResponse)
async def get_clients(
    pagination: dict = Depends(get_pagination_params),
    sorting: dict = Depends(get_sorting_params),
    search: Optional[str] = Query(None, description="Search term for company or contact name"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    platform: Optional[str] = Query(None, description="Filter by platform preference"),
    assigned_user_id: Optional[int] = Query(None, description="Filter by assigned user"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response (e.g., 'id,company_name,email')"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a paginated list of clients with optional filtering and sorting.
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
    
    # Apply sorting
    sort_by = sorting["sort_by"]
    sort_order = sorting["sort_order"]
    if sort_by:
        if hasattr(Client, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(Client, sort_by).desc())
            else:
                query = query.order_by(getattr(Client, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    # Apply pagination
    skip = pagination["skip"]
    limit = pagination["limit"]
    total = query.count()
    clients = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        processed_clients = []
        for client in clients:
            client_dict = client.__dict__.copy()
            filtered_client = {k: v for k, v in client_dict.items() if k in selected_fields}
            processed_clients.append(filtered_client)
        clients = processed_clients
    else:
        clients = [ClientResponse.from_orm(client) for client in clients]
    
    # Calculate pagination values directly
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    # Return the response directly
    return {
        "clients": clients,
        "total": total,
        "page": page,
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

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
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
    update_data = client_data.model_dump(exclude_unset=True)
    # Map 'notes' to 'general_notes' if present
    if 'notes' in update_data:
        update_data['general_notes'] = update_data.pop('notes')
    
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_database_session),
    current_user: User = Depends(get_current_user)
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
