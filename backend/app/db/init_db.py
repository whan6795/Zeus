"""
Database initialization script
Creates tables and seeds initial data
"""
from sqlalchemy.exc import IntegrityError
from app.db.database import engine, SessionLocal, Base
from app.db.models import User, Permission
from app.scripts.script_registry import register_scripts


def init_db():
    """Initialize database with tables and seed data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create permissions with ON CONFLICT handling
        permissions = {
            "module1": {"name": "module1", "description": "Patient Data Analysis"},
            "module2": {"name": "module2", "description": "Medical Image Processing"},
            "module3": {"name": "module3", "description": "Drug Interaction Analysis"}
        }
        
        permission_objs = {}
        for key, perm_data in permissions.items():
            try:
                # Try to get existing permission
                perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
                if not perm:
                    # Create new permission
                    perm = Permission(**perm_data)
                    db.add(perm)
                    db.commit()
                    db.refresh(perm)
                permission_objs[key] = perm
            except IntegrityError:
                db.rollback()
                # If conflict, get the existing permission
                perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
                permission_objs[key] = perm
        
        # Create users with permissions
        # Password for all users: "secret"
        # Using the same hash as in the original code for compatibility
        hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
        
        users_data = [
            {
                "username": "admin",
                "hashed_password": hashed_password,
                "permissions": [permission_objs["module1"], permission_objs["module2"], permission_objs["module3"]]
            },
            {
                "username": "user1",
                "hashed_password": hashed_password,
                "permissions": [permission_objs["module1"], permission_objs["module2"]]
            },
            {
                "username": "user2",
                "hashed_password": hashed_password,
                "permissions": [permission_objs["module3"]]
            }
        ]
        
        for user_data in users_data:
            try:
                # Check if user already exists
                existing_user = db.query(User).filter(User.username == user_data["username"]).first()
                if not existing_user:
                    user = User(
                        username=user_data["username"],
                        hashed_password=user_data["hashed_password"],
                        permissions=user_data["permissions"]
                    )
                    db.add(user)
                    db.commit()
            except IntegrityError:
                db.rollback()
                # User already exists, skip
                continue
        
        print("Database initialized successfully with seed data")
        
        # Register scripts
        register_scripts(db)
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
