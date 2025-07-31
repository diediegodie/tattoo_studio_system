"""
Database package for Tattoo Studio Management System.

This package contains all database models and CRUD operations.
"""

from .models.base import Base, db as engine, get_session, close_session
from .models import (
    User,
    Client,
    Artist,
    Session,
    create_user,
    read_user,
    read_user_by_name,
    update_user,
    delete_user,
    list_all_users,
    create_client,
    read_client,
    update_client,
    delete_client,
    list_all_clients,
    create_artist,
    read_artist,
    update_artist,
    delete_artist,
    list_all_artists,
    create_session,
    read_session,
    update_session,
    delete_session,
    list_all_sessions,
)


def initialize_database():
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        from utils.logger import setup_logger

        logger = setup_logger(__name__)
        logger.info("Database initialized successfully")
    except Exception as e:
        from utils.logger import setup_logger

        logger = setup_logger(__name__)
        logger.error(f"Error initializing database: {e}")
        raise


__all__ = [
    "Base",
    "engine",
    "get_session",
    "close_session",
    "initialize_database",
    "User",
    "Client",
    "Artist",
    "Session",
    "create_user",
    "read_user",
    "read_user_by_name",
    "update_user",
    "delete_user",
    "list_all_users",
    "create_client",
    "read_client",
    "update_client",
    "delete_client",
    "list_all_clients",
    "create_artist",
    "read_artist",
    "update_artist",
    "delete_artist",
    "list_all_artists",
    "create_session",
    "read_session",
    "update_session",
    "delete_session",
    "list_all_sessions",
]
