"""
Reusable API dependencies for filtering, sorting, and pagination.
"""

from fastapi import Query
from typing import Optional

def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
):
    """
    Returns pagination parameters (skip, limit).
    """
    return {"skip": skip, "limit": limit}

def get_sorting_params(
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order ('asc' or 'desc')"),
):
    """
    Returns sorting parameters (sort_by, sort_order).
    """
    return {"sort_by": sort_by, "sort_order": sort_order}
