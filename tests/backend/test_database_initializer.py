"""
Unit tests for services.database_initializer.initialize_database

Covers:
- Normal case: all tables missing
- Edge case: some tables exist
- Failure case: DB locked/permission error

Run with pytest.
"""

import os
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import OperationalError
from backend.database import models
from services.database_initializer import initialize_database

TEST_DB_PATH = "test_initializer.db"
TEST_DB_URI = f"sqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="function")
def temp_db(monkeypatch):
    # Setup: create a new SQLite DB for each test
    engine = create_engine(TEST_DB_URI)
    monkeypatch.setattr("services.database_initializer.engine", engine)
    models.Base.metadata.drop_all(bind=engine)
    yield engine
    # Teardown: remove test DB file
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_initialize_database_normal(temp_db):
    # All tables missing: should create all
    result = initialize_database()
    assert result["status"] == "SUCCESS"
    assert isinstance(result["created_tables"], list)
    assert set(result["created_tables"]) == set(models.Base.metadata.tables.keys())

    # Tables now exist
    inspector = inspect(temp_db)
    for table in models.Base.metadata.tables:
        assert inspector.has_table(table)


def test_initialize_database_edge(temp_db):
    # Create one table manually
    tables = list(models.Base.metadata.tables.values())
    tables[0].create(bind=temp_db)
    # Now run initializer
    result = initialize_database()
    # Should only create missing tables
    assert result["status"] == "SUCCESS"
    if isinstance(result["created_tables"], list):
        assert tables[0].name not in result["created_tables"]
    # All tables should exist
    inspector = inspect(temp_db)
    for table in models.Base.metadata.tables:
        assert inspector.has_table(table)


def test_initialize_database_failure(monkeypatch):
    # Simulate DB locked/permission error
    def broken_engine(*args, **kwargs):
        raise OperationalError("DB is locked", None, None)

    monkeypatch.setattr("services.database_initializer.engine", broken_engine)
    result = initialize_database()
    assert result["status"] == "FAILURE"
    assert "error" in result
