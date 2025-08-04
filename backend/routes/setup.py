from backend.routes.role_decorators import admin_required

"""
Flask route for initial database setup (idempotent) and health check.

POST /api/setup/database
- Only available in DEBUG mode for safety.
- Calls the database_initializer service and returns a JSON summary.

GET /health
- Health check endpoint for monitoring
"""

from flask import Blueprint, jsonify, current_app, abort
from services.database_initializer import initialize_database
from automations.backup_flow import daily_backup_flow, BACKUP_DIR
from configs.config import AppConfig
from datetime import datetime
from backend.database.models.base import db as global_db, get_session

setup_bp = Blueprint("setup", __name__)


@setup_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for monitoring and integration tests.
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "app": "Tattoo Studio Manager",
            }
        ),
        200,
    )


@admin_required
@setup_bp.route("/api/setup/database", methods=["POST"])
def setup_database():
    """
    Idempotent endpoint to initialize database tables.
    Only available in debug mode.
    """
    config = AppConfig()  # Read env vars at request time
    if not config.DEBUG:
        abort(
            403, description="Database setup endpoint is only available in debug mode."
        )

    # Ensure the application's database engine is initialized
    engine = global_db
    if engine is None:
        from backend.database.models.base import init_engine

        # Reason: Handle edge case where DB_URL is invalid or mock
        if not isinstance(config.DB_URL, str) or not config.DB_URL:
            return (
                jsonify(
                    {
                        "status": "FAILURE",
                        "error": "Database engine not initialized: Invalid or missing DB_URL for engine initialization",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                500,
            )
        try:
            init_engine(config.DB_URL)
            from backend.database.models.base import db as refreshed_db

            engine = refreshed_db
        except Exception as e:
            return (
                jsonify(
                    {
                        "status": "FAILURE",
                        "error": f"Engine initialization error: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                500,
            )
        if engine is None:
            return (
                jsonify(
                    {
                        "status": "FAILURE",
                        "error": "Application database engine is not initialized",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                500,
            )

    # Get a session for potential commit operations
    session = get_session()

    try:
        result = initialize_database(engine=engine, session=session)
        return jsonify(result), 200 if result["status"] == "SUCCESS" else 500
    finally:
        # Always close the session
        if session:
            session.close()

@admin_required
@setup_bp.route("/api/backup/database", methods=["POST"])
def backup_database():
    """
    Endpoint to trigger database backup and rotation.
    Only available to admin users.
    """
    import os
    try:
        daily_backup_flow()
        # Find today's backup file
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        backup_file = f"{today}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_file)
        if os.path.exists(backup_path):
            return jsonify({"status": "SUCCESS", "backup_file": backup_file}), 200
        else:
            return jsonify({"status": "FAILURE", "error": "Backup file not created"}), 500
    except Exception as e:
        return jsonify({"status": "FAILURE", "error": str(e)}), 500
