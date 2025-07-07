"""Tests for utility functions."""

import pytest
from datetime import datetime, timedelta
import json
from pathlib import Path
import os

from app.utils.pagination import paginate_results
from app.utils.date_utils import format_date, calculate_date_difference, is_date_in_range
from app.utils.file_utils import ensure_directory_exists, generate_unique_filename
from app.utils.validation import validate_email, validate_phone_number
from app.utils.security import hash_password, verify_password

# Pagination tests
def test_paginate_results():
    """Test pagination utility function."""
    # Create a list of 20 items
    items = [i for i in range(1, 21)]
    
    # Test default pagination (page 1, 10 items per page)
    paginated = paginate_results(items)
    assert paginated["items"] == [i for i in range(1, 11)]
    assert paginated["total"] == 20
    assert paginated["page"] == 1
    assert paginated["size"] == 10
    assert paginated["pages"] == 2
    
    # Test custom page and size
    paginated = paginate_results(items, page=2, size=5)
    assert paginated["items"] == [i for i in range(6, 11)]
    assert paginated["total"] == 20
    assert paginated["page"] == 2
    assert paginated["size"] == 5
    assert paginated["pages"] == 4
    
    # Test empty list
    paginated = paginate_results([])
    assert paginated["items"] == []
    assert paginated["total"] == 0
    assert paginated["page"] == 1
    assert paginated["size"] == 10
    assert paginated["pages"] == 0
    
    # Test page out of range
    paginated = paginate_results(items, page=5)
    assert paginated["items"] == []
    assert paginated["total"] == 20
    assert paginated["page"] == 5
    assert paginated["size"] == 10
    assert paginated["pages"] == 2

# Date utility tests
def test_format_date():
    """Test date formatting utility function."""
    # Test with datetime object
    date = datetime(2023, 9, 15, 14, 30, 0)
    assert format_date(date) == "2023-09-15"
    assert format_date(date, format="%Y/%m/%d") == "2023/09/15"
    assert format_date(date, format="%d-%m-%Y") == "15-09-2023"
    assert format_date(date, format="%B %d, %Y") == "September 15, 2023"
    
    # Test with string date
    assert format_date("2023-09-15") == "2023-09-15"
    assert format_date("2023-09-15", format="%Y/%m/%d") == "2023/09/15"
    
    # Test with invalid date
    with pytest.raises(ValueError):
        format_date("invalid-date")

def test_calculate_date_difference():
    """Test date difference calculation utility function."""
    # Test with datetime objects
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2023, 9, 15)
    assert calculate_date_difference(start_date, end_date) == 14
    
    # Test with string dates
    assert calculate_date_difference("2023-09-01", "2023-09-15") == 14
    
    # Test with mixed types
    assert calculate_date_difference(start_date, "2023-09-15") == 14
    assert calculate_date_difference("2023-09-01", end_date) == 14
    
    # Test with end date before start date
    assert calculate_date_difference(end_date, start_date) == -14
    
    # Test with same date
    assert calculate_date_difference(start_date, start_date) == 0
    
    # Test with invalid date
    with pytest.raises(ValueError):
        calculate_date_difference("invalid-date", end_date)

def test_is_date_in_range():
    """Test date range check utility function."""
    # Test with datetime objects
    date = datetime(2023, 9, 10)
    start_date = datetime(2023, 9, 1)
    end_date = datetime(2023, 9, 15)
    assert is_date_in_range(date, start_date, end_date) is True
    
    # Test with string dates
    assert is_date_in_range("2023-09-10", "2023-09-01", "2023-09-15") is True
    
    # Test with mixed types
    assert is_date_in_range(date, "2023-09-01", "2023-09-15") is True
    assert is_date_in_range("2023-09-10", start_date, end_date) is True
    
    # Test with date outside range
    assert is_date_in_range("2023-08-31", start_date, end_date) is False
    assert is_date_in_range("2023-09-16", start_date, end_date) is False
    
    # Test with date at range boundaries
    assert is_date_in_range(start_date, start_date, end_date) is True
    assert is_date_in_range(end_date, start_date, end_date) is True
    
    # Test with invalid date
    with pytest.raises(ValueError):
        is_date_in_range("invalid-date", start_date, end_date)

# File utility tests
def test_ensure_directory_exists(tmpdir):
    """Test directory creation utility function."""
    # Test with existing directory
    dir_path = tmpdir.mkdir("existing_dir")
    assert ensure_directory_exists(str(dir_path)) == str(dir_path)
    assert os.path.exists(str(dir_path))
    
    # Test with new directory
    new_dir = os.path.join(str(tmpdir), "new_dir")
    assert ensure_directory_exists(new_dir) == new_dir
    assert os.path.exists(new_dir)
    
    # Test with nested directory
    nested_dir = os.path.join(str(tmpdir), "parent", "child", "grandchild")
    assert ensure_directory_exists(nested_dir) == nested_dir
    assert os.path.exists(nested_dir)

def test_generate_unique_filename(tmpdir):
    """Test unique filename generation utility function."""
    # Test with non-existing file
    base_dir = str(tmpdir)
    filename = "test.txt"
    unique_filename = generate_unique_filename(base_dir, filename)
    assert unique_filename == os.path.join(base_dir, filename)
    
    # Create the file and test again
    with open(os.path.join(base_dir, filename), "w") as f:
        f.write("test")
    
    unique_filename = generate_unique_filename(base_dir, filename)
    assert unique_filename != os.path.join(base_dir, filename)
    assert unique_filename.startswith(os.path.join(base_dir, "test"))
    assert unique_filename.endswith(".txt")
    assert "_" in os.path.basename(unique_filename)
    
    # Test with different file extension
    pdf_filename = "report.pdf"
    unique_pdf = generate_unique_filename(base_dir, pdf_filename)
    assert unique_pdf == os.path.join(base_dir, pdf_filename)
    
    # Create the file and test again
    with open(os.path.join(base_dir, pdf_filename), "w") as f:
        f.write("test")
    
    unique_pdf = generate_unique_filename(base_dir, pdf_filename)
    assert unique_pdf != os.path.join(base_dir, pdf_filename)
    assert unique_pdf.startswith(os.path.join(base_dir, "report"))
    assert unique_pdf.endswith(".pdf")

# Validation tests
def test_validate_email():
    """Test email validation utility function."""
    # Test valid emails
    assert validate_email("user@example.com") is True
    assert validate_email("user.name@example.co.uk") is True
    assert validate_email("user+tag@example.org") is True
    
    # Test invalid emails
    assert validate_email("user@") is False
    assert validate_email("@example.com") is False
    assert validate_email("user@example") is False
    assert validate_email("user@.com") is False
    assert validate_email("user@exam ple.com") is False
    assert validate_email("") is False
    assert validate_email(None) is False

def test_validate_phone_number():
    """Test phone number validation utility function."""
    # Test valid phone numbers
    assert validate_phone_number("555-123-4567") is True
    assert validate_phone_number("(555) 123-4567") is True
    assert validate_phone_number("555.123.4567") is True
    assert validate_phone_number("5551234567") is True
    assert validate_phone_number("+1 555-123-4567") is True
    
    # Test invalid phone numbers
    assert validate_phone_number("555-123") is False
    assert validate_phone_number("555-123-45678") is False
    assert validate_phone_number("abc-def-ghij") is False
    assert validate_phone_number("") is False
    assert validate_phone_number(None) is False

# Security tests
def test_password_hashing():
    """Test password hashing and verification."""
    password = "SecurePassword123!"
    
    # Test hashing
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0
    
    # Test verification with correct password
    assert verify_password(password, hashed) is True
    
    # Test verification with incorrect password
    assert verify_password("WrongPassword", hashed) is False
    assert verify_password("", hashed) is False
    
    # Test with different passwords
    password2 = "AnotherPassword456!"
    hashed2 = hash_password(password2)
    assert hashed2 != hashed
    assert verify_password(password2, hashed2) is True
    assert verify_password(password, hashed2) is False