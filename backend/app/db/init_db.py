"""
Database initialization script
Creates tables and seeds initial data
"""
from app.db.database import engine, SessionLocal, Base
from app.db.models import User, Permission
from app.core.security import get_password_hash


def init_db():
    """Initialize database with tables and seed data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already initialized, skipping seed data")
            return
        
        # Create permissions
        permissions = {
            "module1": Permission(name="module1", description="Patient Data Analysis"),
            "module2": Permission(name="module2", description="Medical Image Processing"),
            "module3": Permission(name="module3", description="Drug Interaction Analysis")
        }
        
        for perm in permissions.values():
            db.add(perm)
        db.commit()
        
        # Reload permissions to get IDs
        for key in permissions:
            db.refresh(permissions[key])
        
        # Create users with permissions
        # Password for all users: "secret"
        hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
        
        admin_user = User(
            username="admin",
            hashed_password=hashed_password,
            permissions=[permissions["module1"], permissions["module2"], permissions["module3"]]
        )
        db.add(admin_user)
        
        user1 = User(
            username="user1",
            hashed_password=hashed_password,
            permissions=[permissions["module1"], permissions["module2"]]
        )
        db.add(user1)
        
        user2 = User(
            username="user2",
            hashed_password=hashed_password,
            permissions=[permissions["module3"]]
        )
        db.add(user2)
        
        db.commit()
        print("Database initialized successfully with seed data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
