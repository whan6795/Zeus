from pydantic import BaseModel
from typing import List, Optional


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None
    permissions: List[str] = []


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class UserInfo(BaseModel):
    """User info schema"""
    username: str
    permissions: List[str]


class TaskCreate(BaseModel):
    """Task creation schema"""
    module_name: str
    parameters: dict = {}


class TaskStatus(BaseModel):
    """Task status schema"""
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
