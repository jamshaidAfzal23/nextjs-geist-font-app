"""
API endpoints for authentication.
This module contains login, logout, and token refresh endpoints.
"""

from ...core.limiter import limiter
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...auth.auth import (create_access_token, create_refresh_token,
                          verify_password)
from ...core.database import get_database_session
from ...core.security import get_current_user
from ...models.user_model import User
from ...schemas.token_schemas import Token
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database_session),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    expires_at = datetime.utcnow() + timedelta(minutes=30)  # Match your token expiration time

    return {"access_token": access_token, "token_type": "bearer", "expires_at": expires_at}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database_session)
):
    """
    Refresh the access token for the current authenticated user.
    """
    # Create a new access token for the current user
    access_token = create_access_token(data={"sub": current_user.email})
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    return {"access_token": access_token, "token_type": "bearer", "expires_at": expires_at}


from ...schemas.user_schemas import PasswordResetRequest, PasswordReset

@router.post("/password-reset-request")
async def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_database_session)):
    """
    Request a password reset for a user.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # To prevent user enumeration, we don't reveal that the user doesn't exist.
        # In a real application, you would send an email with a password reset link.
        return {"message": "If an account with that email exists, a password reset link has been sent."}

    # In a real application, you would generate a password reset token, save it to the database,
    # and send it to the user's email address.
    # For now, we'll just return a dummy message.
    return {"message": "Password reset email sent"}


@router.post("/reset-password")
async def reset_password(request: PasswordReset, db: Session = Depends(get_database_session)):
    """
    Reset a user's password using a token.
    """
    # In a real application, you would verify the password reset token and find the associated user.
    # For now, we'll just return a dummy message.
    return {"message": "Password has been reset"}


@router.post("/logout")
async def logout():
    """
    Logout the current user.
    In a stateless JWT implementation, logout is typically handled client-side
    by simply discarding the token. This endpoint exists for API completeness.
    """
    return {"message": "Successfully logged out"}
