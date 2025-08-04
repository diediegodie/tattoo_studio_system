"""
Test Alembic migration system:
- Runs migrations in a test SQLite DB
- Checks for expected tables
- Optionally, checks autogenerate for new model changes
"""

import os
import sqlite3
import pytest
from alembic.config import Config
from alembic import command

TEST_DB_PATH = "test_migration.db"
ALEMBIC_INI = os.path.abspath("alembic.ini")
EXPECTED_TABLES = {"users", "clients", "artists", "sessions"}


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_db():
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_alembic_migration_creates_tables():
    # Setup Alembic config for test DB
    cfg = Config(ALEMBIC_INI)
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{TEST_DB_PATH}")
    # Run upgrade to head
    command.upgrade(cfg, "head")
    # Check tables
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = set(row[0] for row in cursor.fetchall())
    conn.close()
    missing = EXPECTED_TABLES - tables
    assert not missing, f"Missing tables after migration: {missing}"


# Optionally, add a test for autogenerate if model changes are made
# def test_alembic_autogenerate_detects_changes():
#     ...
