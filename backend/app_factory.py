"""
Application Factory for the Flask App.
"""

import logging
from typing import Optional
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

    # Load config at runtime to ensure environment variables are fresh
    from configs.config import AppConfig

    config = AppConfig()

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

    # For live server tests (frontend/integration), we need to initialize the database
    # even when TESTING=1 if using a file-based database
    is_memory_db = ":memory:" in db_url
    skip_db_init = os.environ.get("TESTING") == "1" and db is not None and is_memory_db

    if not skip_db_init:
        # Initialize database engine and session
        init_engine(db_url)
        init_session()

        # Create tables if they don't exist (important for live server tests)
        from services.database_initializer import initialize_database
        from backend.database.models.base import db, get_session

        if db is not None:
            try:
                # Reason: For file-based SQLite, ensure database file is writable
                if "sqlite" in db_url and not ":memory:" in db_url:
                    import os

                    db_file = db_url.replace("sqlite:///", "")
                    if db_file and os.path.exists(db_file):
                        # Ensure the database file is writable
                        import stat

                        current_permissions = os.stat(db_file).st_mode
                        os.chmod(
                            db_file, current_permissions | stat.S_IWUSR | stat.S_IWGRP
                        )
                        logging.info(f"Ensured database file is writable: {db_file}")

                initialize_database(engine=db, session=get_session())
                logging.info("Database tables initialized successfully")
            except Exception as e:
                logging.warning(
                    f"Database initialization failed (tables may already exist): {e}"
                )

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
