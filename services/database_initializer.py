"""
Database initializer service for Tattoo Studio Management System.

Provides an idempotent function to ensure all required tables exist.
Uses SQLAlchemy metadata to check and create tables as needed.
Logs all actions and returns a summary of created/existing tables.

Follows project structure and logging conventions.
"""

from sqlalchemy import inspect
from backend.database.models.base import Base
from utils.logger import setup_logger
from datetime import datetime
from configs.config import config

logger = setup_logger(__name__)


def initialize_database(engine=None, session=None):
    """
    Ensures all required tables exist in the database.

    Args:
        engine: SQLAlchemy engine instance. If None, raises ValueError.
        session: SQLAlchemy session instance. Optional, used for commit operations.

    Returns:
        dict: {
            "status": "SUCCESS" or "FAILURE",
            "created_tables": list of created tables or "ALREADY EXISTS",
            "timestamp": ISO8601 string
        }

    Raises:
        ValueError: If engine is None
    """
    if engine is None:
        raise ValueError(
            "Database engine cannot be None. Please provide a valid SQLAlchemy engine."
        )

    logger.info(f"[DatabaseInitializer] Initializing database with engine: {engine}")

    created_tables = []
    already_exists = []
    try:
        inspector = inspect(engine)
        metadata = Base.metadata
        for table_name, table in metadata.tables.items():
            if inspector.has_table(table_name):
                already_exists.append(table_name)
                logger.info(f"Table '{table_name}' already exists.")
            else:
                table.create(bind=engine)
                created_tables.append(table_name)
                logger.info(f"Created table '{table_name}'.")

        # If session is provided, commit the changes
        if session is not None:
            session.commit()
            logger.info("Database changes committed via provided session.")

        if created_tables:
            status = "SUCCESS"
        else:
            status = "SUCCESS"  # Still success if all tables already exist

        result = {
            "status": status,
            "created_tables": created_tables if created_tables else "ALREADY EXISTS",
            "timestamp": datetime.now().isoformat(),
        }
        logger.info(f"Database initialization result: {result}")
        return result

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return {
            "status": "FAILURE",
            "created_tables": [],
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
