"""
Flask route for initial database setup (idempotent).

POST /api/setup/database
- Only available in DEBUG mode for safety.
- Calls the database_initializer service and returns a JSON summary.
"""

from flask import Blueprint, jsonify, current_app, abort
from services.database_initializer import initialize_database
from configs.config import AppConfig

setup_bp = Blueprint("setup", __name__)


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
    result = initialize_database()
    return jsonify(result), 200 if result["status"] == "SUCCESS" else 500
