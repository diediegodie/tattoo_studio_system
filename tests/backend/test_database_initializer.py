"""
Unit tests for services.database_initializer.initialize_database

Covers:
- Normal case: all tables missing
- Edge case: some tables exist
- Failure case: DB locked/permission error
- Error case: engine is None

Run with pytest.
"""

import os
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from backend.database.models.base import Base
from services.database_initializer import initialize_database

TEST_DB_PATH = "test_initializer.db"
TEST_DB_URI = f"sqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="function")
def temp_engine():
    """Create a temporary database engine for each test."""
    engine = create_engine(TEST_DB_URI)
    Base.metadata.drop_all(bind=engine)
    yield engine
    # Teardown: remove test DB file
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def temp_session(temp_engine):
    """Create a temporary session for each test."""
    SessionLocal = sessionmaker(bind=temp_engine)
    session = SessionLocal()
    yield session
    session.close()


def test_initialize_database_normal(temp_engine, temp_session):
    """Test initialize_database with all tables missing - normal case."""
    # All tables missing: should create all
    result = initialize_database(engine=temp_engine, session=temp_session)

    assert result["status"] == "SUCCESS"
    assert isinstance(result["created_tables"], list)
    assert set(result["created_tables"]) == set(Base.metadata.tables.keys())

    # Tables now exist
    inspector = inspect(temp_engine)
    for table in Base.metadata.tables:
        assert inspector.has_table(table)


def test_initialize_database_edge(temp_engine, temp_session):
    """Test initialize_database with some tables existing - edge case."""
    # Create one table manually
    tables = list(Base.metadata.tables.values())
    if tables:  # Only run if we have tables to create
        tables[0].create(bind=temp_engine)

        # Now run initializer
        result = initialize_database(engine=temp_engine, session=temp_session)

        # Should only create missing tables
        assert result["status"] == "SUCCESS"
        if isinstance(result["created_tables"], list):
            assert tables[0].name not in result["created_tables"]

        # All tables should exist
        inspector = inspect(temp_engine)
        for table in Base.metadata.tables:
            assert inspector.has_table(table)


def test_initialize_database_all_exist(temp_engine, temp_session):
    """Test initialize_database when all tables already exist - edge case."""
    # Create all tables first
    Base.metadata.create_all(bind=temp_engine)

    # Now run initializer
    result = initialize_database(engine=temp_engine, session=temp_session)

    # Should report all tables already exist
    assert result["status"] == "SUCCESS"
    assert result["created_tables"] == "ALREADY EXISTS"


def test_initialize_database_engine_none():
    """Test initialize_database with engine=None - failure case."""
    with pytest.raises(ValueError, match="Database engine cannot be None"):
        initialize_database(engine=None)


def test_initialize_database_session_none(temp_engine):
    """Test initialize_database with session=None - normal case."""
    # Should work fine without session
    result = initialize_database(engine=temp_engine, session=None)
    assert result["status"] == "SUCCESS"

    # Tables should be created
    inspector = inspect(temp_engine)
    for table in Base.metadata.tables:
        assert inspector.has_table(table)


def test_initialize_database_failure(monkeypatch, temp_session):
    """Test initialize_database with broken engine - failure case."""

    # Create a mock engine that raises an exception during inspect
    class BrokenEngine:
        def __init__(self):
            pass

        def __str__(self):
            return "BrokenEngine"

    def broken_inspect(engine):
        raise OperationalError("DB is locked", {}, Exception("DB is locked"))

    monkeypatch.setattr("services.database_initializer.inspect", broken_inspect)

    broken_engine = BrokenEngine()
    result = initialize_database(engine=broken_engine, session=temp_session)

    assert result["status"] == "FAILURE"
    assert "error" in result
    assert "DB is locked" in result["error"]
