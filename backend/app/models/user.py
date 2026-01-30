from typing import List
from sqlalchemy.orm import Session
from app.db import models


class User:
    """User model adapter for compatibility with existing code"""
    def __init__(self, username: str, hashed_password: str, permissions: List[str], user_id: int = None):
        self.username = username
        self.hashed_password = hashed_password
        self.permissions = permissions
        self.id = user_id


def get_user(db: Session, username: str) -> User:
    """Get user by username from database"""
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        return None
    
    # Convert to User object for compatibility
    permissions = [perm.name for perm in db_user.permissions]
    return User(
        username=db_user.username,
        hashed_password=db_user.hashed_password,
        permissions=permissions,
        user_id=db_user.id
    )


def get_user_id(db: Session, username: str) -> int:
    """Get user ID by username from database"""
    db_user = db.query(models.User).filter(models.User.username == username).first()
    return db_user.id if db_user else None
