from typing import List


class User:
    """In-memory user model for simplicity"""
    def __init__(self, username: str, hashed_password: str, permissions: List[str]):
        self.username = username
        self.hashed_password = hashed_password
        self.permissions = permissions


# Simulated user database
users_db = {
    "admin": User(
        username="admin",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        permissions=["module1", "module2", "module3"]
    ),
    "user1": User(
        username="user1",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        permissions=["module1", "module2"]
    ),
    "user2": User(
        username="user2",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        permissions=["module3"]
    )
}


def get_user(username: str) -> User:
    """Get user by username"""
    return users_db.get(username)
