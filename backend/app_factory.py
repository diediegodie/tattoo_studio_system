from configs.config import config
from typing import Optional

"""
Application Factory for the Flask App.
"""

import logging
from flask import Flask
from backend.routes.client import client_bp
from backend.routes.artist import artist_bp
from backend.routes.session import session_bp
from backend.routes.user import user_bp
from backend.routes.setup import setup_bp
from backend.database.models.base import init_engine, init_session


def create_app(config_overrides: Optional[dict] = None):
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)

    # Load default config and override if necessary
    app.config.from_object(config)
    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    db_url = app.config.get("DB_URL", "sqlite:///default.db")
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Initializing app with DB_URL: {db_url}")

    # Initialize database engine and session only if not in testing mode with existing setup
    import os
    from backend.database.models.base import db

    if not (os.environ.get("TESTING") == "1" and db is not None):
        # Initialize database engine and session
        init_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
        )
        init_session()

    # JWT Setup
    from flask_jwt_extended import JWTManager
    from backend.routes.auth import auth_bp

    app.config["JWT_SECRET_KEY"] = app.config.get("JWT_SECRET_KEY", "super-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    jwt = JWTManager(app)

    # Register Blueprints
    app.register_blueprint(client_bp)
    app.register_blueprint(artist_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(setup_bp)
    app.register_blueprint(auth_bp)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"success": False, "error": "Endpoint not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {"success": False, "error": "Method not allowed"}, 405

    return app
