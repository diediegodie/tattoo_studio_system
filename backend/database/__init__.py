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


def initialize_database(engine=None, session=None):
    """
    Initialize the database by creating all tables.

    Args:
        engine: SQLAlchemy engine instance. If None, tries to use global engine.
        session: SQLAlchemy session instance. Optional.

    Raises:
        ValueError: If no engine is available
    """
    # Import the actual function from services
    from services.database_initializer import initialize_database as _initialize_db

    # If no engine provided, try to use the global engine
    if engine is None:
        engine = globals().get("engine")
        if engine is None:
            from .models.base import init_engine, init_session
            from configs.config import config

            init_engine(config.DB_URL)
            init_session()
            engine = globals().get("engine")

    return _initialize_db(engine=engine, session=session)


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
