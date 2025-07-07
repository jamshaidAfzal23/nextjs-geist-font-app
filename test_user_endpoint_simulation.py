import os
import sys

# Add the parent directory to sys.path to allow imports from the application
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

# Import the pagination function
from backend_restructured.app.utils.pagination import paginate_results

# Simulate the user_endpoints.py functionality
def simulate_get_users(page=1, size=10, search=None, role=None, is_active=None):
    # Create a simulated database of users
    users_db = [
        {"id": 1, "full_name": "Admin User", "email": "admin@example.com", "role": "admin", "is_active": True},
        {"id": 2, "full_name": "Regular User", "email": "user@example.com", "role": "user", "is_active": True},
        {"id": 3, "full_name": "Test User 1", "email": "test1@example.com", "role": "user", "is_active": True},
        {"id": 4, "full_name": "Test User 2", "email": "test2@example.com", "role": "user", "is_active": False},
        {"id": 5, "full_name": "Manager User", "email": "manager@example.com", "role": "manager", "is_active": True},
        {"id": 6, "full_name": "Developer User", "email": "dev@example.com", "role": "developer", "is_active": True},
        {"id": 7, "full_name": "Inactive Admin", "email": "inactive@example.com", "role": "admin", "is_active": False},
    ]
    
    # Apply filters
    filtered_users = users_db
    
    if search:
        search = search.lower()
        filtered_users = [u for u in filtered_users if 
                         search in u["full_name"].lower() or 
                         search in u["email"].lower()]
    
    if role:
        filtered_users = [u for u in filtered_users if u["role"] == role]
    
    if is_active is not None:
        filtered_users = [u for u in filtered_users if u["is_active"] == is_active]
    
    # Get total count
    total = len(filtered_users)
    
    # Use the pagination utility directly instead of manual slicing
    return paginate_results(
        items=filtered_users,
        page=page,
        size=size,
        total=total
    )

# Test cases
print("\nTest 1: Default parameters (page=1, size=10)")
result1 = simulate_get_users()
print(f"Items count: {len(result1['items'])}")
print(f"Total: {result1['total']}")
print(f"Page: {result1['page']}")
print(f"Size: {result1['size']}")
print(f"Pages: {result1['pages']}")

# Test with page=1, size=3 to see first page
print("\nTest 2a: First page (page=1, size=3)")
result2a = simulate_get_users(page=1, size=3)
print(f"Items count: {len(result2a['items'])}")
print(f"Items: {[u['full_name'] for u in result2a['items']]}")
print(f"Total: {result2a['total']}")
print(f"Page: {result2a['page']}")
print(f"Size: {result2a['size']}")
print(f"Pages: {result2a['pages']}")

# Test with page=2, size=3 to see second page
print("\nTest 2b: Second page (page=2, size=3)")
result2b = simulate_get_users(page=2, size=3)
print(f"Items count: {len(result2b['items'])}")
print(f"Items: {[u['full_name'] for u in result2b['items']]}")
print(f"Total: {result2b['total']}")
print(f"Page: {result2b['page']}")
print(f"Size: {result2b['size']}")
print(f"Pages: {result2b['pages']}")

# Test with page=3, size=3 to see third page
print("\nTest 2c: Third page (page=3, size=3)")
result2c = simulate_get_users(page=3, size=3)
print(f"Items count: {len(result2c['items'])}")
print(f"Items: {[u['full_name'] for u in result2c['items']]}")
print(f"Total: {result2c['total']}")
print(f"Page: {result2c['page']}")
print(f"Size: {result2c['size']}")
print(f"Pages: {result2c['pages']}")

print("\nTest 3: Filter by role (role='admin')")
result3 = simulate_get_users(role="admin")
print(f"Items count: {len(result3['items'])}")
print(f"Items: {[u['full_name'] for u in result3['items']]}")
print(f"Total: {result3['total']}")
print(f"Page: {result3['page']}")
print(f"Size: {result3['size']}")
print(f"Pages: {result3['pages']}")

print("\nTest 4: Filter by active status (is_active=True)")
result4 = simulate_get_users(is_active=True)
print(f"Items count: {len(result4['items'])}")
print(f"Items: {[u['full_name'] for u in result4['items']]}")
print(f"Total: {result4['total']}")
print(f"Page: {result4['page']}")
print(f"Size: {result4['size']}")
print(f"Pages: {result4['pages']}")

print("\nTest 5: Search by name (search='user')")
result5 = simulate_get_users(search="user")
print(f"Items count: {len(result5['items'])}")
print(f"Items: {[u['full_name'] for u in result5['items']]}")
print(f"Total: {result5['total']}")
print(f"Page: {result5['page']}")
print(f"Size: {result5['size']}")
print(f"Pages: {result5['pages']}")

print("\nTest 6: Combined filters (role='admin', is_active=False)")
result6 = simulate_get_users(role="admin", is_active=False)
print(f"Items count: {len(result6['items'])}")
print(f"Items: {[u['full_name'] for u in result6['items']]}")
print(f"Total: {result6['total']}")
print(f"Page: {result6['page']}")
print(f"Size: {result6['size']}")
print(f"Pages: {result6['pages']}")

print("\nAll tests completed successfully!")