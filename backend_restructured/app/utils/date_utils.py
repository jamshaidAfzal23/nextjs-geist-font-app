"""Date utility functions."""

from datetime import datetime

def format_date(date, format="%Y-%m-%d"):
    """Format a date string or datetime object.
    
    Args:
        date: Date string or datetime object
        format: Date format string
        
    Returns:
        str: Formatted date string
        
    Raises:
        ValueError: If date string is invalid
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    return date.strftime(format)

def calculate_date_difference(start_date, end_date):
    """Calculate the difference between two dates in days.
    
    Args:
        start_date: Start date string or datetime object
        end_date: End date string or datetime object
        
    Returns:
        int: Number of days between dates
        
    Raises:
        ValueError: If date string is invalid
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    return (end_date - start_date).days

def is_date_in_range(date, start_date, end_date):
    """Check if a date is within a given range.
    
    Args:
        date: Date to check
        start_date: Start of range
        end_date: End of range
        
    Returns:
        bool: True if date is within range, False otherwise
        
    Raises:
        ValueError: If date string is invalid
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    return start_date <= date <= end_date