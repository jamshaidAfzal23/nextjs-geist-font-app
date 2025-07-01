"""
API Key service for the Smart CRM SaaS application.
This module contains functions for managing API keys.
"""

import secrets
from sqlalchemy.orm import Session
from ..models.api_key_model import APIKey

def create_api_key(db: Session, user_id: int) -> APIKey:
    """Create a new API key for a user."""
    key = secrets.token_urlsafe(32)
    api_key = APIKey(key=key, user_id=user_id)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key

def get_api_key(db: Session, key: str) -> APIKey:
    """Get an API key by its value."""
    return db.query(APIKey).filter(APIKey.key == key).first()

def revoke_api_key(db: Session, key: str) -> bool:
    """Revoke an API key."""
    api_key = get_api_key(db, key)
    if api_key:
        db.delete(api_key)
        db.commit()
        return True
    return False
