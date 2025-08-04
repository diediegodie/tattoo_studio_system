"""
Prefect flow for daily SQLite database backup.
- Copies the main DB file to /backups/YYYYMMDD.db
- Rotates old backups (keeps last 7 days)
- Logs all actions
"""

import os
import shutil
import logging
from datetime import datetime, timedelta
from prefect import flow, task

DB_PATH = os.path.join(os.path.dirname(__file__), "../backend/database/test.db")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "../backups")
RETENTION_DAYS = 7


@task
def backup_db():
    """Copy DB file to backups/YYYYMMDD.db"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found: {DB_PATH}")
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    today = datetime.now().strftime("%Y%m%d")
    backup_file = os.path.join(BACKUP_DIR, f"{today}.db")
    shutil.copy2(DB_PATH, backup_file)
    logging.info(f"Backup created: {backup_file}")
    return backup_file


@task
def rotate_backups():
    """Delete backups older than RETENTION_DAYS"""
    now = datetime.now()
    for fname in os.listdir(BACKUP_DIR):
        if fname.endswith(".db"):
            try:
                date_str = fname.replace(".db", "")
                file_date = datetime.strptime(date_str, "%Y%m%d")
                age = (now - file_date).days
                if age >= RETENTION_DAYS:
                    os.remove(os.path.join(BACKUP_DIR, fname))
                    logging.info(f"Deleted old backup: {fname}")
            except Exception as e:
                logging.warning(f"Could not parse backup filename: {fname} ({e})")


@flow(name="Daily DB Backup")
def daily_backup_flow():
    backup_db()
    rotate_backups()


if __name__ == "__main__":
    daily_backup_flow()
