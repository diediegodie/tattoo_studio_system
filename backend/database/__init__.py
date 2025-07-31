"""
Database package for Tattoo Studio Management System.

This package contains all database models and CRUD operations.
"""

from .models import (
    User,
    initialize_database,
    create_user,
    read_user,
    read_user_by_name,
    update_user,
    delete_user,
    list_all_users,
    get_session,
    close_session,
    db as engine,  # Expose db as engine for compatibility
)

__all__ = [
    "User",
    "initialize_database",
    "create_user",
    "read_user",
    "read_user_by_name",
    "update_user",
    "delete_user",
    "list_all_users",
    "get_session",
    "close_session",
    "engine",
]
