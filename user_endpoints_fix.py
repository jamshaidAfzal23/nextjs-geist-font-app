import os
import sys

# Add the parent directory to sys.path to allow imports from the application
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

"""
Fix for the user_endpoints.py file

The issue is in the get_users function where pagination is applied twice:
1. First at the database query level with query.offset(skip).limit(limit)
2. Then again when using paginate_results

Here's the specific code change needed:
"""

print("\nFix for user_endpoints.py - Option 1 (More efficient, direct approach):\n")
print('''
@router.get("/", response_model=UserListResponse)
async def get_users(
    pagination: dict = Depends(get_pagination_params),
    sorting: dict = Depends(get_sorting_params),
    search: Optional[str] = Query(None, description="Search term for name or email"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response (e.g., 'id,full_name,email')"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a paginated list of users with optional filtering, sorting, and field selection.
    """
    query = db.query(User)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_filter)) |
            (User.email.ilike(search_filter))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Apply sorting
    sort_by = sorting["sort_by"]
    sort_order = sorting["sort_order"]
    if sort_by:
        if hasattr(User, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(User, sort_by).desc())
            else:
                query = query.order_by(getattr(User, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    skip = pagination["skip"]
    limit = pagination["limit"]
    users = query.offset(skip).limit(limit).all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        # Filter the dictionary representation of each user
        processed_users = []
        for user in users:
            user_dict = user.__dict__.copy()
            filtered_user = {k: v for k, v in user_dict.items() if k in selected_fields}
            processed_users.append(filtered_user)
        users = processed_users
    else:
        # If no fields are specified, return the full UserResponse schema
        users = [UserResponse.from_orm(user) for user in users]
    
    # Calculate pagination values directly
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 0
    
    # Return the response directly
    return {
        "items": users,
        "total": total,
        "page": page,
        "size": limit,
        "pages": pages
    }
''')

print("\nFix for user_endpoints.py - Option 2 (Using paginate_results utility):\n")
print('''
@router.get("/", response_model=UserListResponse)
async def get_users(
    pagination: dict = Depends(get_pagination_params),
    sorting: dict = Depends(get_sorting_params),
    search: Optional[str] = Query(None, description="Search term for name or email"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response (e.g., 'id,full_name,email')"),
    db: Session = Depends(get_database_session)
):
    """
    Retrieve a paginated list of users with optional filtering, sorting, and field selection.
    """
    query = db.query(User)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_filter)) |
            (User.email.ilike(search_filter))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Apply sorting
    sort_by = sorting["sort_by"]
    sort_order = sorting["sort_order"]
    if sort_by:
        if hasattr(User, sort_by):
            if sort_order == "desc":
                query = query.order_by(getattr(User, sort_by).desc())
            else:
                query = query.order_by(getattr(User, sort_by).asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field: {sort_by}"
            )

    # Get total count
    total = query.count()
    
    # Get all users matching the filters (without pagination)
    all_users = query.all()

    # Apply field selection
    if fields:
        selected_fields = [field.strip() for field in fields.split(',')]
        # Filter the dictionary representation of each user
        processed_users = []
        for user in all_users:
            user_dict = user.__dict__.copy()
            filtered_user = {k: v for k, v in user_dict.items() if k in selected_fields}
            processed_users.append(filtered_user)
        all_users = processed_users
    else:
        # If no fields are specified, return the full UserResponse schema
        all_users = [UserResponse.from_orm(user) for user in all_users]
    
    # Calculate page from skip/limit
    skip = pagination["skip"]
    limit = pagination["limit"]
    page = (skip // limit) + 1 if limit > 0 else 1
    
    # Use the pagination utility to format the response
    from ...utils.pagination import paginate_results
    return paginate_results(
        items=all_users,
        page=page,
        size=limit,
        total=total
    )
''')

print("\nNote: Option 1 is more efficient for large datasets as it only loads the required records from the database.")
print("Option 2 loads all matching records into memory, which could be inefficient for large datasets.")
print("Choose the appropriate solution based on your expected dataset size and performance requirements.")