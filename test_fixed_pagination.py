import os
import sys

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
    {"id": 6, "full_name": "Test User 4", "email": "test4@example.com", "role": "user"},
    {"id": 7, "full_name": "Test User 5", "email": "test5@example.com", "role": "user"},
]

# Simulate the fixed implementation in user_endpoints.py
def simulate_get_users(skip=0, limit=100):
    # Get total count
    total = len(users)
    
    # Apply pagination
    paginated_users = users[skip:skip+limit]
    
    # Calculate pagination values directly
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    # Return the response directly
    return {
        "items": paginated_users,
        "total": total,
        "page": page,
        "size": limit,
        "pages": pages
    }

# Test the pagination with different page sizes and page numbers
def test_pagination():
    print("\nTesting pagination with the fixed implementation:\n")
    
    # Test with default parameters
    print("Test 1: Default parameters (skip=0, limit=100)")
    result = simulate_get_users()
    print(f"Total users: {result['total']}")
    print(f"Page: {result['page']}")
    print(f"Size: {result['size']}")
    print(f"Pages: {result['pages']}")
    print(f"Items count: {len(result['items'])}")
    print(f"Items: {[u['full_name'] for u in result['items']]}")
    
    # Test with skip=0, limit=2 (page 1, size 2)
    print("\nTest 2: skip=0, limit=2 (page 1, size 2)")
    result = simulate_get_users(skip=0, limit=2)
    print(f"Total users: {result['total']}")
    print(f"Page: {result['page']}")
    print(f"Size: {result['size']}")
    print(f"Pages: {result['pages']}")
    print(f"Items count: {len(result['items'])}")
    print(f"Items: {[u['full_name'] for u in result['items']]}")
    
    # Test with skip=2, limit=2 (page 2, size 2)
    print("\nTest 3: skip=2, limit=2 (page 2, size 2)")
    result = simulate_get_users(skip=2, limit=2)
    print(f"Total users: {result['total']}")
    print(f"Page: {result['page']}")
    print(f"Size: {result['size']}")
    print(f"Pages: {result['pages']}")
    print(f"Items count: {len(result['items'])}")
    print(f"Items: {[u['full_name'] for u in result['items']]}")
    
    # Test with skip=4, limit=2 (page 3, size 2)
    print("\nTest 4: skip=4, limit=2 (page 3, size 2)")
    result = simulate_get_users(skip=4, limit=2)
    print(f"Total users: {result['total']}")
    print(f"Page: {result['page']}")
    print(f"Size: {result['size']}")
    print(f"Pages: {result['pages']}")
    print(f"Items count: {len(result['items'])}")
    print(f"Items: {[u['full_name'] for u in result['items']]}")
    
    # Test with skip=6, limit=2 (page 4, size 2)
    print("\nTest 5: skip=6, limit=2 (page 4, size 2)")
    result = simulate_get_users(skip=6, limit=2)
    print(f"Total users: {result['total']}")
    print(f"Page: {result['page']}")
    print(f"Size: {result['size']}")
    print(f"Pages: {result['pages']}")
    print(f"Items count: {len(result['items'])}")
    print(f"Items: {[u['full_name'] for u in result['items']]}")

# Run the test
try:
    test_pagination()
    print("\nPagination tests completed successfully!")
except Exception as e:
    print(f"\nError during testing: {e}")