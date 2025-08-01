"""
Test file for Flask backend API.

Tests the integration between Flask endpoints and database operations.
Following the project guidelines for comprehensive testing.
"""

import pytest
import json
import pytest
import json
from unittest.mock import patch
from backend.app_factory import create_app
from services.database_initializer import initialize_database
from backend.database.models.base import Base


@pytest.fixture
def client(test_engine, test_session):
    """Create a test client for the Flask app with proper database setup."""
    Base.metadata.create_all(bind=test_engine)
    app = create_app()
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


class TestFlaskAPI:
    """Test cases for Flask API endpoints."""

    def test_setup_database_normal_case(self, client, test_engine):
        """Test normal case: database setup endpoint in debug mode."""
        # Reason: Ensure endpoint works and returns success JSON

        # Mock the global_db and get_session to use our test engine
        with patch("backend.routes.setup.global_db", test_engine):
            with patch("backend.routes.setup.get_session") as mock_get_session:
                from sqlalchemy.orm import sessionmaker

                SessionLocal = sessionmaker(bind=test_engine)
                session = SessionLocal()
                mock_get_session.return_value = session

                with patch("backend.routes.setup.AppConfig") as mock_config:
                    mock_config.return_value.DEBUG = True

                    response = client.post("/api/setup/database")
                    data = json.loads(response.data)
                    assert response.status_code == 200
                    assert data["status"] == "SUCCESS"
                    assert "timestamp" in data
                    assert "created_tables" in data

                session.close()

    def test_setup_database_edge_case_already_exists(self, client, test_engine):
        """Test edge case: endpoint called when tables already exist."""

        # Pre-create tables
        from backend.database.models.base import Base

        Base.metadata.create_all(bind=test_engine)

        # Mock the global_db and get_session to use our test engine
        with patch("backend.routes.setup.global_db", test_engine):
            with patch("backend.routes.setup.get_session") as mock_get_session:
                from sqlalchemy.orm import sessionmaker

                SessionLocal = sessionmaker(bind=test_engine)
                session = SessionLocal()
                mock_get_session.return_value = session

                with patch("backend.routes.setup.AppConfig") as mock_config:
                    mock_config.return_value.DEBUG = True

                    response = client.post("/api/setup/database")
                    data = json.loads(response.data)
                    assert response.status_code == 200
                    assert data["status"] == "SUCCESS"
                    assert data["created_tables"] == "ALREADY EXISTS"

                session.close()

    def test_setup_database_failure_case_not_debug(self, client, test_engine):
        """Test failure case: endpoint not available if not in debug mode."""

        # Mock the global_db and get_session to use our test engine
        with patch("backend.routes.setup.global_db", test_engine):
            with patch("backend.routes.setup.get_session") as mock_get_session:
                from sqlalchemy.orm import sessionmaker

                SessionLocal = sessionmaker(bind=test_engine)
                session = SessionLocal()
                mock_get_session.return_value = session

                with patch("backend.routes.setup.AppConfig") as mock_config:
                    mock_config.return_value.DEBUG = False

                    response = client.post("/api/setup/database")
                    assert response.status_code == 403
                    # Flask abort returns HTML by default, so no JSON expected

                session.close()

    def test_health_check_normal_case(self, client):
        """Test the health check endpoint."""
        # Reason: Verify basic app functionality
        response = client.get("/health")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["app"] == "Tattoo Studio Manager"

    def test_create_user_normal_case(self, isolated_test_session, test_engine):
        """Test creating a user - normal case."""
        # Reason: Ensure user creation API works correctly

        # Create app with test configuration
        app = create_app()
        app.config["TESTING"] = True
        app.config["DEBUG"] = True

        with app.test_client() as client:
            with app.app_context():
                # Override database connections
                import backend.database.models.base as base

                original_db = base.db
                original_session = base.session

                base.db = test_engine
                base.session = isolated_test_session

                try:
                    response = client.post(
                        "/api/users",
                        data=json.dumps(
                            {
                                "name": "John Doe",
                                "email": "john.doe@example.com",
                                "password": "securepass123",
                                "role": "staff",
                                "birth": 1990,
                            }
                        ),
                        content_type="application/json",
                    )

                    assert response.status_code == 201
                    data = json.loads(response.data)
                    assert data["success"] is True
                    assert data["user"]["name"] == "John Doe"
                    assert data["user"]["birth"] == 1990
                finally:
                    # Restore original database connections
                    base.db = original_db
                    base.session = original_session

    def test_create_user_failure_case(self, client):
        """Test creating a user with invalid data - failure case."""
        # Reason: Ensure proper error handling for bad input
        response = client.post(
            "/api/users",
            data=json.dumps({"invalid": "data"}),  # Missing required 'name' field
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["success"] is False
        assert "error" in data

    def test_get_user_by_id_edge_case(self, client):
        """Test getting a user with non-existent ID - edge case."""
        # Reason: Ensure proper error handling for missing users
        response = client.get("/api/users/99999")  # Non-existent ID

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False
        assert "error" in data

    def test_search_user_failure_case(self, client):
        """Test searching for non-existent user - failure case."""
        # Reason: Ensure proper error handling for user not found
        response = client.get("/api/users/search/NonExistentUser")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False
        assert "error" in data

    def test_404_endpoint(self, client):
        """Test 404 error handling - edge case."""
        # Reason: Ensure proper error handling for non-existent endpoints
        response = client.get("/api/nonexistent")

        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"] == "Endpoint not found"

    def test_method_not_allowed(self, client):
        """Test 405 error handling - edge case."""
        # Reason: Ensure proper error handling for unsupported methods
        response = client.patch("/api/users")  # PATCH not allowed

        assert response.status_code == 405
        data = json.loads(response.data)
        assert data["success"] is False
        assert data["error"] == "Method not allowed"
