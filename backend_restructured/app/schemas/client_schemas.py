"""
Client schemas for Smart CRM SaaS application.
This module defines Pydantic models for client data validation and serialization.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class ClientBase(BaseModel):
    """
    Base client schema with common fields.
    
    Attributes:
        company_name (str): Official company or business name
        contact_person_name (str): Primary contact person's name
        email (EmailStr): Primary email address for communication
        phone_number (str): Primary phone number
        address (str): Complete business address
        industry (str): Industry or business sector
        platform_preference (str): Preferred platform for projects
        notes (str): Additional notes about the client
    """
    company_name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Official company or business name"
    )
    contact_person_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the primary contact person"
    )
    email: EmailStr = Field(
        ...,
        description="Primary email address for client communication"
    )
    phone_number: Optional[str] = Field(
        None,
        max_length=20,
        description="Primary phone number for client contact"
    )
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="Complete business address"
    )
    industry: Optional[str] = Field(
        None,
        max_length=100,
        description="Industry or business sector"
    )
    platform_preference: Optional[str] = Field(
        None,
        max_length=100,
        description="Preferred platform for projects"
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Client category"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional notes about the client"
    )

class ClientCreate(ClientBase):
    """
    Schema for creating a new client.
    
    Includes assigned_user_id to specify which user will manage this client.
    """
    assigned_user_id: int = Field(
        ...,
        description="ID of the user who will manage this client",
        example=1
    )

class ClientCreateBulk(BaseModel):
    clients: List[ClientCreate]

class ClientUpdate(BaseModel):
    """
    Schema for updating client information.
    
    All fields are optional for partial updates.
    """
    id: Optional[int] = Field(
        None,
        description="Client ID for bulk operations"
    )
    company_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        description="Updated company name"
    )
    contact_person_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Updated contact person name"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Updated email address"
    )
    phone_number: Optional[str] = Field(
        None,
        max_length=20,
        description="Updated phone number"
    )
    address: Optional[str] = Field(
        None,
        max_length=500,
        description="Updated address"
    )
    industry: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated industry"
    )
    platform_preference: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated platform preference"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Updated notes"
    )
    assigned_user_id: Optional[int] = Field(
        None,
        description="Updated assigned user ID"
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Updated client category"
    )

class ClientUpdateBulk(BaseModel):
    clients: List[ClientUpdate]

class ClientDeleteBulk(BaseModel):
    client_ids: List[int]

class ClientResponse(ClientBase):
    """
    Schema for client data in API responses.
    
    Includes all client information with computed fields.
    """
    id: int = Field(..., description="Unique client identifier")
    assigned_user_id: int = Field(..., description="ID of the assigned user")
    created_at: datetime = Field(..., description="When the client was added")
    updated_at: datetime = Field(..., description="When the client was last updated")
    
    # Computed fields (these would be calculated in the API layer)
    total_project_value: Optional[float] = Field(
        None,
        description="Total value of all projects for this client"
    )
    active_projects_count: Optional[int] = Field(
        None,
        description="Number of active projects"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClientListResponse(BaseModel):
    """
    Schema for paginated client list responses.
    
    Contains list of clients with pagination metadata.
    """
    clients: List[ClientResponse] = Field(..., description="List of clients")
    total: int = Field(..., description="Total number of clients")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of clients per page")

class ClientSummary(BaseModel):
    """
    Schema for client summary information.
    
    Contains essential client information for dropdowns and quick references.
    """
    id: int = Field(..., description="Client ID")
    company_name: str = Field(..., description="Company name")
    contact_person_name: str = Field(..., description="Contact person name")
    email: str = Field(..., description="Email address")
    active_projects_count: int = Field(..., description="Number of active projects")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

class ClientSearchFilters(BaseModel):
    """
    Schema for client search and filtering parameters.
    
    Contains optional filters for client queries.
    """
    search_term: Optional[str] = Field(
        None,
        max_length=100,
        description="Search term for company name or contact person"
    )
    industry: Optional[str] = Field(
        None,
        description="Filter by industry"
    )
    assigned_user_id: Optional[int] = Field(
        None,
        description="Filter by assigned user"
    )
    platform_preference: Optional[str] = Field(
        None,
        description="Filter by platform preference"
    )
    has_active_projects: Optional[bool] = Field(
        None,
        description="Filter clients with active projects"
    )
    created_after: Optional[datetime] = Field(
        None,
        description="Filter clients created after this date"
    )
    created_before: Optional[datetime] = Field(
        None,
        description="Filter clients created before this date"
    )

class ClientStats(BaseModel):
    """
    Schema for client statistics and analytics.
    
    Contains aggregated data about clients.
    """
    total_clients: int = Field(..., description="Total number of clients", example=100)
    active_clients: int = Field(..., description="Clients with active projects", example=50)
    clients_by_industry: dict = Field(..., description="Client count by industry", example={"Technology": 30, "Finance": 20})
    clients_by_user: dict = Field(..., description="Client count by assigned user", example={"1": 60, "2": 40})
    average_project_value: float = Field(..., description="Average project value per client", example=7500.50)
    top_clients_by_value: List[dict] = Field(..., description="Top clients by total project value", example=[{"id": 1, "name": "Acme Corp", "total_value": 25000.00}])
