"""File utility functions."""

import os
from datetime import datetime

def ensure_directory_exists(directory_path):
    """Create a directory if it doesn't exist.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        str: Path to directory
    """
    os.makedirs(directory_path, exist_ok=True)
    return directory_path

def generate_unique_filename(directory, filename):
    """Generate a unique filename in the given directory.
    
    Args:
        directory: Directory path
        filename: Original filename
        
    Returns:
        str: Unique file path
    """
    base, ext = os.path.splitext(filename)
    filepath = os.path.join(directory, filename)
    
    counter = 1
    while os.path.exists(filepath):
        new_filename = f"{base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{counter}{ext}"
        filepath = os.path.join(directory, new_filename)
        counter += 1
    
    return filepath