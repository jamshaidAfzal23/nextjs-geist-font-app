"""Pagination utility functions."""

from typing import List, Dict, Any

def paginate_results(items: List[Any], page: int = 1, size: int = 10, total: int = None) -> Dict[str, Any]:
    """Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Page number (1-based)
        size: Number of items per page
        total: Total number of items (optional, calculated from items if not provided)
        
    Returns:
        dict: Paginated results containing:
            - items: List of items for the current page
            - total: Total number of items
            - page: Current page number
            - size: Number of items per page
            - pages: Total number of pages
    """
    # Handle empty list
    if not items:
        return {
            "items": [],
            "total": 0,
            "page": 1,
            "size": size,
            "pages": 0
        }
    
    # Use provided total or calculate from items
    if total is None:
        total = len(items)
    pages = (total + size - 1) // size
    
    # Adjust page number if out of range
    if page < 1:
        page = 1
    
    # Calculate start and end indices
    start = (page - 1) * size
    end = start + size
    
    # Return empty list if page is out of range
    if start >= total:
        return {
            "items": [],
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
    
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "size": size,
        "pages": pages
    }