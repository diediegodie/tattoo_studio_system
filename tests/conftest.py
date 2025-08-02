import os

# Ensure test_integration.db is deleted before integration tests
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "../test_integration.db")
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

"""
Pytest configuration for test isolation.
Creates a global in-memory SQLite database for all tests with proper isolation.
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configs.config import AppConfig

# Ensure project root is in sys.path for all test imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from backend.database.models import base


@pytest.fixture(scope="session")
def test_engine():
    """
    Session-scoped test database engine.

    Creates a single database engine for all tests in the session.
    It uses an in-memory SQLite database by default, but can be overridden
    by setting the DB_URL environment variable (e.g., for integration tests).
    """
    # Set test environment variables
    os.environ["TESTING"] = "1"

    # Create test config instance to get the DB_URL
    test_config = AppConfig()
    db_url = test_config.DB_URL

    # Create engine with test-friendly settings
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL debugging
    )

    print(f"[conftest] Test engine created with DB_URL: {db_url}")

    yield engine

    # Cleanup after all tests complete
    try:
        engine.dispose()
        print("[conftest] Test engine cleanup complete")
    except Exception as e:
        print(f"[conftest] Error during engine cleanup: {e}")


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """
    Session-scoped session factory for tests.
    """
    SessionLocal = sessionmaker(bind=test_engine)
    return SessionLocal


@pytest.fixture(scope="function")
def test_session(test_engine, test_session_factory):
    """
    Function-scoped test session with transaction rollback for isolation.

    Each test gets a fresh session with automatic rollback at the end.
    """
    # Create all tables for each test
    base.Base.metadata.create_all(bind=test_engine)

    # Create a connection and transaction
    connection = test_engine.connect()
    transaction = connection.begin()

    # Create session bound to the connection
    session = test_session_factory(bind=connection)

    yield session

    # Rollback transaction and close connection for isolation
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def isolated_test_session(test_engine):
    """
    Function-scoped isolated test session for complete test isolation.

    This creates tables, provides a session, then drops all tables after the test.
    Use this for tests that need complete isolation.
    """
    # Create all tables
    base.Base.metadata.create_all(bind=test_engine)

    # Create session factory
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()

    yield session

    # Clean up
    session.close()
    # Drop all tables for complete isolation
    base.Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(test_engine):
    """
    Auto-used fixture to set up global test database state.

    Sets the global engine in base module for compatibility with existing code.
    """
    # Set the global engine in base module
    base.db = test_engine

    # Create session factory
    SessionLocal = sessionmaker(bind=test_engine)
    base.Session = SessionLocal
    base.session = SessionLocal()

    print(f"[conftest] Test database setup complete")

    yield

    # Cleanup after all tests complete
    try:
        if base.session:
            base.session.close()
        print("[conftest] Test database cleanup complete")
    except Exception as e:
        print(f"[conftest] Error during cleanup: {e}")


def pytest_configure(config):
    """
    Pytest configuration hook to set up test environment before test collection.
    """
    # Ensure test environment is set early
    os.environ["TESTING"] = "1"

    # For frontend tests, preserve any existing DB_URL (file-based) from the test script
    # For other tests, use in-memory DB for speed and isolation
    if "DB_URL" not in os.environ:
        # Check if we're running frontend or integration tests
        import sys

        test_args = " ".join(sys.argv)
        if "tests/frontend" in test_args or "tests/integration" in test_args:
            # Use file-based database for frontend/integration tests
            # Use an absolute path to avoid ambiguity
            db_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../test_integration.db")
            )
            os.environ["DB_URL"] = f"sqlite:///{db_path}"
        else:
            # Use in-memory database for backend tests
            os.environ["DB_URL"] = "sqlite:///:memory:"

    print(f"[pytest_configure] TESTING=1, DB_URL={os.environ['DB_URL']}")


@pytest.fixture
def initialize_test_database():
    """
    Fixture to provide database initialization function for tests.

    Returns a function that can initialize the database with provided engine/session.
    """
    from services.database_initializer import initialize_database

    return initialize_database
