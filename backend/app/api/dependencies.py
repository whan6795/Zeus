from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import oauth2_scheme, decode_access_token
from app.models.user import get_user, User
from app.db.database import get_db
from typing import List


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = get_user(db, username)
    if user is None:
        raise credentials_exception
    
    return user


def require_permission(required_permission: str):
    """Dependency to check if user has required permission"""
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {required_permission}"
            )
        return current_user
    return permission_checker


def require_script_permission(module_name: str, script_name: str):
    """Dependency to check if user has required script permission"""
    async def script_permission_checker(current_user: User = Depends(get_current_user)) -> User:
        script_key = f"{module_name}.{script_name}"
        
        # Check script-level permission
        if script_key not in current_user.script_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required script permission: {script_key}"
            )
        return current_user
    return script_permission_checker
