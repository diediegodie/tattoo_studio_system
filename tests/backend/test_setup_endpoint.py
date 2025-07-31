"""
Tests for the setup endpoint (/api/setup/database).

Demonstrates correct use of initialize_database with engine and session parameters.
Ensures that tables are created in the correct test database and not in the global version.

Run with pytest.
"""

import pytest
import json
from unittest.mock import patch
from backend.app_factory import create_app
from backend.database.models.base import Base
from sqlalchemy import inspect


class TestSetupEndpoint:
    """Test cases for the database setup endpoint."""

    @pytest.fixture
    def test_app(self, test_engine):
        """Create test app with test engine."""
        # Create app with test configuration
        app = create_app(
            config_overrides={
                "TESTING": True,
                "DEBUG": True,
                "DB_URL": "sqlite:///:memory:",
            }
        )

        # Override the global engine with our test engine
        with patch("backend.routes.setup.global_db", test_engine):
            with patch("backend.routes.setup.get_session") as mock_get_session:
                # Create a test session
                from sqlalchemy.orm import sessionmaker

                SessionLocal = sessionmaker(bind=test_engine)
                test_session = SessionLocal()
                mock_get_session.return_value = test_session

                yield app, test_session

                test_session.close()

    def test_setup_database_endpoint_normal_case(self, test_app, test_engine):
        """Test the setup database endpoint - normal case."""
        app, test_session = test_app

        with app.test_client() as client:
            # Mock the AppConfig to ensure DEBUG=True in the endpoint
            with patch("backend.routes.setup.AppConfig") as mock_config:
                mock_config.return_value.DEBUG = True

                # Make request to setup endpoint
                response = client.post("/api/setup/database")

                # Check response status and content
                assert response.status_code == 200

                data = json.loads(response.data)
                assert data["status"] == "SUCCESS"
                assert "created_tables" in data
                assert "timestamp" in data

                # Verify tables were created in test database
                inspector = inspect(test_engine)
                for table_name in Base.metadata.tables.keys():
                    assert inspector.has_table(
                        table_name
                    ), f"Table {table_name} should exist"

    def test_setup_database_endpoint_tables_exist(self, test_app, test_engine):
        """Test the setup database endpoint when tables already exist - edge case."""
        app, test_session = test_app

        # Pre-create all tables
        Base.metadata.create_all(bind=test_engine)

        with app.test_client() as client:
            # Mock the AppConfig to ensure DEBUG=True in the endpoint
            with patch("backend.routes.setup.AppConfig") as mock_config:
                mock_config.return_value.DEBUG = True

                # Make request to setup endpoint
                response = client.post("/api/setup/database")

                # Check response status and content
                assert response.status_code == 200

                data = json.loads(response.data)
                assert data["status"] == "SUCCESS"
                assert data["created_tables"] == "ALREADY EXISTS"

    def test_setup_database_endpoint_engine_none(self, test_app):
        """Test the setup database endpoint with no engine - failure case."""
        app, test_session = test_app

        with app.test_client() as client:
            with patch("backend.routes.setup.global_db", None):
                with patch("backend.routes.setup.AppConfig") as mock_config:
                    mock_config.return_value.DEBUG = True

                    # Make request to setup endpoint
                    response = client.post("/api/setup/database")

                    # Check response status and content
                    assert response.status_code == 500

                    data = json.loads(response.data)
                    assert data["status"] == "FAILURE"
                    assert "error" in data
                    assert "not initialized" in data["error"]

    def test_setup_database_endpoint_not_debug_mode(self, test_app):
        """Test the setup database endpoint in non-debug mode - failure case."""
        app, test_session = test_app

        with app.test_client() as client:
            with patch("backend.routes.setup.AppConfig") as mock_config:
                # Mock config to return DEBUG=False
                mock_config.return_value.DEBUG = False

                # Make request to setup endpoint
                response = client.post("/api/setup/database")

                # Check response status and content
                assert response.status_code == 403

                # Flask abort returns HTML for 403, not JSON, so check content type
                assert (
                    "text/html" in response.content_type
                    or "html" in response.get_data(as_text=True).lower()
                )

    def test_health_check_endpoint(self, test_app):
        """Test the health check endpoint - normal case."""
        app, test_session = test_app

        with app.test_client() as client:
            # Make request to health endpoint
            response = client.get("/health")

            # Check response status and content
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert data["app"] == "Tattoo Studio Manager"

    def test_setup_database_endpoint_with_session_commit(self, test_app, test_engine):
        """Test that the setup endpoint properly uses session for commits."""
        app, test_session = test_app

        with app.test_client() as client:
            # Mock the AppConfig to ensure DEBUG=True in the endpoint
            with patch("backend.routes.setup.AppConfig") as mock_config:
                mock_config.return_value.DEBUG = True

                # Make request to setup endpoint
                response = client.post("/api/setup/database")

                # Check response
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data["status"] == "SUCCESS"

                # Verify that the changes were committed by checking in a new session
                from sqlalchemy.orm import sessionmaker

                SessionLocal = sessionmaker(bind=test_engine)
                new_session = SessionLocal()

                try:
                    # Check that tables exist and are accessible
                    inspector = inspect(test_engine)
                    table_count = len(inspector.get_table_names())
                    assert table_count > 0, "Tables should be created and committed"
                finally:
                    new_session.close()
