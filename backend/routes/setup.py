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

    # Get the application's database engine
    engine = global_db
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
