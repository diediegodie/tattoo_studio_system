"""
Database models for Tattoo Studio Management System.

This module defines SQLAlchemy models and CRUD operations for the application.
Following the project structure with feature-based organization.
"""

from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "tattoo_system.db")
db = create_engine(f"sqlite:///{DB_PATH}", echo=False)

Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()


class User(Base):
    """User model for authentication and basic user information."""

    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(100), nullable=False)
    birth = Column("birth", Integer, nullable=True)  # Birth year as integer
    active = Column("active", Boolean, default=True)

    def __init__(self, name, birth=None, active=True):
        """
        Initialize a new User.

        Args:
            name (str): User's full name
            birth (int): Birth year (optional)
            active (bool): Whether the user is active (default: True)
        """
        self.name = name
        self.birth = birth
        self.active = active

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', birth={self.birth})>"


# Create all tables
def initialize_database():
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(bind=db)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


# CRUD operations for User
def create_user(name, birth=None, active=True):
    """
    Create a new user.

    Args:
        name (str): User's full name
        birth (int): Birth year (optional)
        active (bool): Whether the user is active

    Returns:
        User: The created user object
    """
    try:
        user = User(name=name, birth=birth, active=active)
        session.add(user)
        session.commit()
        logger.info(f"User created successfully: {user.name}")
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating user: {e}")
        raise


def read_user(user_id):
    """
    Read a user by ID.

    Args:
        user_id (int): The user's ID

    Returns:
        User: The user object or None if not found
    """
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            logger.info(f"User found: {user.name}")
        else:
            logger.warning(f"User with ID {user_id} not found")
        return user
    except Exception as e:
        logger.error(f"Error reading user: {e}")
        raise


def read_user_by_name(name):
    """
    Read a user by name.

    Args:
        name (str): The user's name

    Returns:
        User: The user object or None if not found
    """
    try:
        user = session.query(User).filter_by(name=name).first()
        if user:
            logger.info(f"User found by name: {user.name}")
        else:
            logger.warning(f"User with name '{name}' not found")
        return user
    except Exception as e:
        logger.error(f"Error reading user by name: {e}")
        raise


def update_user(user_id, **kwargs):
    """
    Update a user's information.

    Args:
        user_id (int): The user's ID
        **kwargs: Fields to update (name, birth, active)

    Returns:
        User: The updated user object or None if not found
    """
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
            logger.info(f"User updated successfully: {user.name}")
            return user
        else:
            logger.warning(f"User with ID {user_id} not found for update")
            return None
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating user: {e}")
        raise


def delete_user(user_id):
    """
    Delete a user by ID.

    Args:
        user_id (int): The user's ID

    Returns:
        bool: True if deleted successfully, False if not found
    """
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            session.delete(user)
            session.commit()
            logger.info(f"User deleted successfully: {user.name}")
            return True
        else:
            logger.warning(f"User with ID {user_id} not found for deletion")
            return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting user: {e}")
        raise


def list_all_users(active_only=True):
    """
    List all users in the database.

    Args:
        active_only (bool): If True, only return active users

    Returns:
        list: List of User objects
    """
    try:
        if active_only:
            users = session.query(User).filter_by(active=True).all()
        else:
            users = session.query(User).all()
        logger.info(f"Retrieved {len(users)} users from database")
        return users
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise


# Database session management
def get_session():
    """Get a new database session."""
    return Session()


def close_session():
    """Close the current session."""
    try:
        session.close()
        logger.info("Database session closed")
    except Exception as e:
        logger.error(f"Error closing session: {e}")
