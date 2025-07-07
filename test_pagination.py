import os
import sys

# Add the parent directory to sys.path to allow imports from the application
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

# Import the pagination function
from backend_restructured.app.utils.pagination import paginate_results

# Create a test list
items = [f"Item {i}" for i in range(1, 21)]  # 20 items

# Test with default parameters
result1 = paginate_results(items)
print("\nTest 1: Default parameters (page=1, size=10)")
print(f"Items: {result1['items']}")
print(f"Total: {result1['total']}")
print(f"Page: {result1['page']}")
print(f"Size: {result1['size']}")
print(f"Pages: {result1['pages']}")

# Test with custom page and size
result2 = paginate_results(items, page=2, size=5)
print("\nTest 2: Custom parameters (page=2, size=5)")
print(f"Items: {result2['items']}")
print(f"Total: {result2['total']}")
print(f"Page: {result2['page']}")
print(f"Size: {result2['size']}")
print(f"Pages: {result2['pages']}")

# Test with empty list
result3 = paginate_results([])
print("\nTest 3: Empty list")
print(f"Items: {result3['items']}")
print(f"Total: {result3['total']}")
print(f"Page: {result3['page']}")
print(f"Size: {result3['size']}")
print(f"Pages: {result3['pages']}")

# Test with page out of range
result4 = paginate_results(items, page=5, size=10)
print("\nTest 4: Page out of range (page=5, size=10)")
print(f"Items: {result4['items']}")
print(f"Total: {result4['total']}")
print(f"Page: {result4['page']}")
print(f"Size: {result4['size']}")
print(f"Pages: {result4['pages']}")

# Test with custom total
result5 = paginate_results(items[:5], page=1, size=5, total=20)
print("\nTest 5: Custom total (items=5, total=20)")
print(f"Items: {result5['items']}")
print(f"Total: {result5['total']}")
print(f"Page: {result5['page']}")
print(f"Size: {result5['size']}")
print(f"Pages: {result5['pages']}")

print("\nAll tests completed successfully!")