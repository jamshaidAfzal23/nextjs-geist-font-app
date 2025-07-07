"""Validation utility functions."""

import re

def validate_email(email):
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone):
    """Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if phone number is valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove all non-numeric characters except + for country code
    cleaned = re.sub(r'[^0-9+]', '', phone)
    
    # Check if the cleaned number matches common formats
    patterns = [
        r'\+?1?\d{10}$',  # +1XXXXXXXXXX or XXXXXXXXXX
        r'\+\d{1,3}\d{10}$'  # +XXX... for international
    ]
    
    return any(bool(re.match(pattern, cleaned)) for pattern in patterns)