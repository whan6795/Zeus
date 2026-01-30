from typing import List


class User:
    """In-memory user model for simplicity
    
    Note: This is a demonstration/development setup. In production:
    1. Use a proper database (PostgreSQL, MySQL, etc.)
    2. Use unique password hashes for each user
    3. Implement proper user management endpoints
    4. Add password reset functionality
    5. Add user registration with email verification
    """
    def __init__(self, username: str, hashed_password: str, permissions: List[str]):
        self.username = username
        self.hashed_password = hashed_password
        self.permissions = permissions


# Simulated user database
# NOTE: All users use the same password hash for demo purposes only
# Password for all users: "secret"
users_db = {
    "admin": User(
        username="admin",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        permissions=["module1", "module2", "module3"]
    ),
    "user1": User(
        username="user1",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        permissions=["module1", "module2"]
    ),
    "user2": User(
        username="user2",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        permissions=["module3"]
    )
}


def get_user(username: str) -> User:
    """Get user by username"""
    return users_db.get(username)
