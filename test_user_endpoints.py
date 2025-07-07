import os
import sys
import json

# Add the parent directory to sys.path to allow imports from the application
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

# Import the pagination function directly
from backend_restructured.app.utils.pagination import paginate_results

# Create a test list of users
users = [
    {"id": 1, "full_name": "Admin User", "email": "admin@example.com", "role": "admin"},
    {"id": 2, "full_name": "Regular User", "email": "user@example.com", "role": "user"},
    {"id": 3, "full_name": "Test User 1", "email": "test1@example.com", "role": "user"},
    {"id": 4, "full_name": "Test User 2", "email": "test2@example.com", "role": "user"},
    {"id": 5, "full_name": "Test User 3", "email": "test3@example.com", "role": "user"},
]

# Test the pagination function with our user list
result = paginate_results(users, page=1, size=10, total=len(users))

print("\nPagination test with users:")
print(f"Items: {result['items']}")
print(f"Total: {result['total']}")
print(f"Page: {result['page']}")
print(f"Size: {result['size']}")
print(f"Pages: {result['pages']}")

# Test with a specific page and size
result2 = paginate_results(users, page=1, size=2, total=len(users))

print("\nPagination test with page=1, size=2:")
print(f"Items: {result2['items']}")
print(f"Total: {result2['total']}")
print(f"Page: {result2['page']}")
print(f"Size: {result2['size']}")
print(f"Pages: {result2['pages']}")

print("\nTest completed!")
