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
    # Reason: For SQLite, configure proper isolation and write capabilities
    if "sqlite" in db_url:
        # SQLite-specific configuration for concurrent write access
        kwargs.setdefault("connect_args", {})
        kwargs["connect_args"].update(
            {
                "check_same_thread": False,
                "isolation_level": None,  # Enable autocommit mode for WAL
                "timeout": 20,  # Increase timeout for concurrent access
            }
        )
        kwargs.setdefault("pool_pre_ping", True)
        kwargs.setdefault("pool_recycle", 3600)

    db = create_engine(db_url, **kwargs)

    # Reason: Configure SQLite for proper WAL mode and write capabilities
    if "sqlite" in db_url:
        from sqlalchemy import event

        @event.listens_for(db, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys=ON")
            # Set busy timeout
            cursor.execute("PRAGMA busy_timeout=30000")
            # Ensure proper synchronization
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()


def init_session():
    """Initializes the database session factory."""
    global Session, session
    # Reason: Configure session with proper SQLite parameters for read-write operations
    if db is not None and "sqlite" in str(db.url):
        # SQLite-specific configuration for concurrent read-write access
        Session = scoped_session(
            sessionmaker(
                bind=db,
                autocommit=False,
                autoflush=False,  # Manual control over when to flush
                expire_on_commit=False,
            )
        )
    else:
        # Default configuration for other databases
        Session = scoped_session(sessionmaker(bind=db))
    session = Session()


def get_session():
    """Get a new database session."""
    if Session is None:
        raise RuntimeError(
            "Session factory is not initialized. Call init_session() first."
        )
    # Reason: For live server, use new session instances to avoid transaction conflicts
    return Session()


def close_session():
    """Close the current session."""
    if session:
        # Reason: remove() should be called on the scoped_session object, not the session instance
        if Session is not None and hasattr(Session, "remove"):
            Session.remove()
        elif hasattr(session, "close"):
            session.close()
