"""
Base model for SQLAlchemy.

This module defines the declarative base, engine, and session for the database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm.scoping import scoped_session
from configs.config import config
import urllib.parse


# These will be initialized by the application factory
db = None
Session = None
session = None

# DB_PATH for logs, backup, and test utilities
DB_PATH = None
if config.DB_URL:
    if config.DB_URL.startswith("sqlite:///"):
        # Extract file path from sqlite URI
        parsed = urllib.parse.urlparse(config.DB_URL)
        DB_PATH = parsed.path.lstrip("/")
    else:
        DB_PATH = config.DB_URL

Base = declarative_base()


def init_engine(db_url, **kwargs):
    """Initializes the database engine."""
    global db
    db = create_engine(db_url, **kwargs)


def init_session():
    """Initializes the database session factory."""
    global Session, session
    Session = scoped_session(sessionmaker(bind=db))
    session = Session()


def get_session():
    """Get a new database session."""
    if Session is None:
        raise RuntimeError("Session factory is not initialized. Call init_session() first.")
    return Session()


def close_session():
    """Close the current session."""
    if session:
        # Reason: remove() should be called on the scoped_session object, not the session instance
        if Session is not None and hasattr(Session, "remove"):
            Session.remove()
        elif hasattr(session, "close"):
            session.close()
