"""
User model and CRUD operations.
"""

from sqlalchemy import Column, String, Integer, Boolean, text
from flask_bcrypt import Bcrypt
from .base import Base, get_session
from utils.logger import setup_logger


logger = setup_logger(__name__)
bcrypt = Bcrypt()


class User(Base):
    """User model for authentication and basic user information."""

    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(100), nullable=False)
    email = Column("email", String(120), unique=True, nullable=False)
    password = Column("password", String(128), nullable=False)
    role = Column("role", String(20), nullable=False, default="staff")  # admin or staff
    birth = Column("birth", Integer, nullable=True)  # Birth year as integer
    active = Column("active", Boolean, default=True)

    def __init__(self, name, email, password, role="staff", birth=None, active=True):
        """
        Initialize a new User.

        Args:
            name (str): User's full name
            email (str): User's email (unique)
            password (str): Plaintext password (will be hashed)
            role (str): User role (admin or staff)
            birth (int): Birth year (optional)
            active (bool): Whether the user is active (default: True)
        """
        self.name = name
        self.email = email
        self.password = self.hash_password(password)
        self.role = role
        self.birth = birth
        self.active = active

    def __repr__(self):
        birth_str = f", birth={self.birth}" if self.birth is not None else ""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}', role='{self.role}'{birth_str})>"

    @staticmethod
    def hash_password(password):
        """Hash a plaintext password using bcrypt."""
        return bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Check a plaintext password against the stored hash."""
        return bcrypt.check_password_hash(self.password, password)


# CRUD operations for User


def create_user(name, email, password, role="staff", birth=None, active=True):
    """
    Create a new user with hashed password.

    Args:
        name (str): User's full name
        email (str): User's email (unique)
        password (str): Plaintext password
        role (str): User role (admin or staff)
        birth (int): Birth year (optional)
        active (bool): Whether the user is active

    Returns:
        User: The created user object
    """
    session = get_session()
    try:
        user = User(
            name=name,
            email=email,
            password=password,
            role=role,
            birth=birth,
            active=active,
        )
        session.add(user)
        session.commit()
        logger.info(f"User created successfully: {user.name} ({user.email})")
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating user: {e}")
        raise
    finally:
        # Reason: Always close the session to prevent connection leaks
        session.close()


def read_user(user_id):
    """
    Read a user by ID.

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        User or None: User object if found, None otherwise.
    """
    import time

    # Retry mechanism for database I/O errors
    max_retries = 3
    retry_delay = 0.1

    for attempt in range(max_retries):
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                logger.info(f"User found: {user.name}")
            else:
                logger.warning(f"User with ID {user_id} not found")
            return user

        except Exception as e:
            logger.error(
                f"Error reading user (attempt {attempt + 1}/{max_retries}): {e}"
            )
            session.rollback()

            # If this is not the last attempt, wait and retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                # Last attempt failed, return None
                return None

        finally:
            session.close()


def read_user_by_email(email):
    """
    Read a user by email.

    Args:
        email (str): The email of the user to retrieve.

    Returns:
        User or None: User object if found, None otherwise.
    """
    import time

    # Retry mechanism for database I/O errors
    max_retries = 3
    retry_delay = 0.1

    for attempt in range(max_retries):
        session = get_session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if user:
                logger.info(f"User found by email: {email}")
            else:
                logger.warning(f"User with email '{email}' not found")
            return user

        except Exception as e:
            logger.error(
                f"Error reading user by email (attempt {attempt + 1}/{max_retries}): {e}"
            )
            session.rollback()

            # If this is not the last attempt, wait and retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                # Last attempt failed, return None
                return None

        finally:
            session.close()


def read_user_by_name(name):
    """
    Read a user by name.

    Args:
        name (str): The user's name

    Returns:
        User: The user object or None if not found
    """
    import time

    # Retry mechanism for database I/O errors
    max_retries = 3
    retry_delay = 0.1

    for attempt in range(max_retries):
        session = get_session()
        try:
            user = session.query(User).filter_by(name=name).first()
            if user:
                logger.info(f"User found by name: {user.name}")
            else:
                logger.warning(f"User with name '{name}' not found")
            return user

        except Exception as e:
            logger.error(
                f"Error reading user by name (attempt {attempt + 1}/{max_retries}): {e}"
            )
            session.rollback()

            # If this is not the last attempt, wait and retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                # Last attempt failed, raise the exception
                raise

        finally:
            session.close()


def update_user(user_id, **kwargs):
    """
    Update a user's information.

    Args:
        user_id (int): The user's ID
        **kwargs: Fields to update (name, birth, active)

    Returns:
        User: The updated user object or None if not found
    """
    import time

    # Retry mechanism for database I/O errors
    max_retries = 3
    retry_delay = 0.1

    for attempt in range(max_retries):
        session = get_session()
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
            logger.error(
                f"Error updating user (attempt {attempt + 1}/{max_retries}): {e}"
            )

            # If this is not the last attempt, wait and retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                # Last attempt failed, raise the exception
                raise

        finally:
            # Reason: Always close the session to prevent connection leaks
            session.close()


def delete_user(user_id):
    """
    Delete a user by ID.

    Args:
        user_id (int): The user's ID

    Returns:
        bool: True if deleted successfully, False if not found
    """
    import time

    # Retry mechanism for database I/O errors
    max_retries = 3
    retry_delay = 0.1

    for attempt in range(max_retries):
        session = get_session()
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
            logger.error(
                f"Error deleting user (attempt {attempt + 1}/{max_retries}): {e}"
            )

            # If this is not the last attempt, wait and retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                # Last attempt failed, raise the exception
                raise

        finally:
            # Reason: Always close the session to prevent connection leaks
            session.close()


def list_all_users(active_only=False):
    """
    List all users with optional filtering.

    Args:
        active_only (bool): If True, only active users are returned.

    Returns:
        list: List of User objects or empty list if error.
    """
    import time

    # Retry mechanism for database I/O errors
    max_retries = 3
    retry_delay = 0.1

    for attempt in range(max_retries):
        session = get_session()
        try:
            # Start with read uncommitted for better concurrent performance
            query = session.query(User)

            if active_only:
                # Use text() to avoid type annotation issues
                query = query.filter(text("active = 1"))

            # Execute with explicit transaction isolation
            session.connection(
                execution_options={"isolation_level": "READ_UNCOMMITTED"}
            )
            users = query.all()

            logger.info(f"Listed {len(users)} users (active_only={active_only})")
            return users

        except Exception as e:
            logger.error(
                f"Error listing users (attempt {attempt + 1}/{max_retries}): {e}"
            )
            session.rollback()

            # If this is not the last attempt, wait and retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                # Last attempt failed, return empty list
                return []

        finally:
            session.close()
