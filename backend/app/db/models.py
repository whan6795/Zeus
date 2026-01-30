from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

# Association table for many-to-many relationship between users and permissions
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# Association table for many-to-many relationship between users and scripts
user_script_permissions = Table(
    'user_script_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('script_id', Integer, ForeignKey('scripts.id'), primary_key=True)
)


class User(Base):
    """User model for database"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    tasks = relationship("Task", back_populates="user")
    script_permissions = relationship("Script", secondary=user_script_permissions, back_populates="users")


class Permission(Base):
    """Permission model for database"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))

    # Relationships
    users = relationship("User", secondary=user_permissions, back_populates="permissions")


class Task(Base):
    """Task model for database - stores task history and results"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)  # Celery task ID
    module_name = Column(String(50), nullable=False)
    script_name = Column(String(100))  # Script name for script-level tracking
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String(20), nullable=False)  # pending, success, failed, etc.
    parameters = Column(JSON)
    result = Column(JSON)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tasks")


class Script(Base):
    """Script model for database - stores available scripts"""
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # Script identifier (e.g., "patient_analysis")
    module_name = Column(String(50), nullable=False)  # Module it belongs to (e.g., "module1")
    display_name = Column(String(200), nullable=False)  # Human-readable name
    description = Column(String(500))
    file_path = Column(String(500), nullable=False)  # Relative path to script file
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", secondary=user_script_permissions, back_populates="script_permissions")

    # Unique constraint: combination of module_name and name must be unique
    __table_args__ = (
        __import__('sqlalchemy').UniqueConstraint('module_name', 'name', name='uq_module_script'),
    )
