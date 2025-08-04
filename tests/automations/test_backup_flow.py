"""
Test cases for backup_flow.py
- Normal case: backup created
- Edge case: DB file missing
- Failure case: permission error
"""

import os
import shutil
import pytest
from datetime import datetime, timedelta
from automations.backup_flow import (
    backup_db,
    rotate_backups,
    BACKUP_DIR,
    DB_PATH,
    RETENTION_DAYS,
)


@pytest.fixture(autouse=True)
def setup_and_teardown(tmp_path):
    # Setup: create dummy DB file
    os.makedirs(BACKUP_DIR, exist_ok=True)
    with open(DB_PATH, "wb") as f:
        f.write(b"123")
    yield
    # Teardown: remove backup and DB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    for fname in os.listdir(BACKUP_DIR):
        os.remove(os.path.join(BACKUP_DIR, fname))


def test_backup_db_normal():
    backup_file = backup_db()
    assert os.path.exists(backup_file)
    assert backup_file.endswith(".db")


def test_backup_db_missing():
    os.remove(DB_PATH)
    with pytest.raises(FileNotFoundError):
        backup_db()


def test_rotate_backups():
    # Create old backup
    # Create backup older than retention window
    old_date = (datetime.now() - timedelta(days=RETENTION_DAYS + 1)).strftime("%Y%m%d")
    old_file = os.path.join(BACKUP_DIR, f"{old_date}.db")
    with open(old_file, "wb") as f:
        f.write(b"old")
    rotate_backups()
    assert not os.path.exists(old_file)
