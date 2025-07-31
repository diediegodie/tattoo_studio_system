"""
Base model for SQLAlchemy.

This module defines the declarative base, engine, and session for the database.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Database configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tattoo_system.db")
db = create_engine(f"sqlite:///{DB_PATH}", echo=False)

Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()


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
