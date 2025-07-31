"""
Test file for Flask backend API.

Tests the integration between Flask endpoints and database operations.
Following the project guidelines for comprehensive testing.
"""

import pytest
import json
import tempfile
import os
from backend.app import app
from backend.database import initialize_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # Create temporary database for testing
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()

    # Configure app for testing
    app.config["TESTING"] = True
    app.config["DEBUG"] = False

    # Override database path for testing
    import backend.database.models.base as base_models

    original_db_path = base_models.DB_PATH
    base_models.DB_PATH = temp_db.name

    # Recreate engine and session with new path
    base_models.db = create_engine(f"sqlite:///{temp_db.name}", echo=False)
    base_models.Session = sessionmaker(bind=base_models.db)
    base_models.session = base_models.Session()

    with app.test_client() as client:
        with app.app_context():
            initialize_database()
        yield client

    # Cleanup
    base_models.session.close()
    base_models.DB_PATH = original_db_path  # Restore original path
    if os.path.exists(temp_db.name):
        os.unlink(temp_db.name)


class TestFlaskAPI:
    """Test cases for Flask API endpoints."""

    def test_setup_database_normal_case(self, client, monkeypatch):
        """Test normal case: database setup endpoint in debug mode."""
        # Reason: Ensure endpoint works and returns success JSON
        monkeypatch.setenv("DEBUG", "true")
        # Reload config in route if needed (if config is cached, may need to patch importlib.reload)
        response = client.post("/api/setup/database")
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["status"] == "SUCCESS"
        assert "timestamp" in data
        assert "created_tables" in data

    def test_setup_database_edge_case_already_exists(self, client, monkeypatch):
        """Test edge case: endpoint called when tables already exist."""
        monkeypatch.setenv("DEBUG", "true")
        # Call twice to ensure idempotency
        client.post("/api/setup/database")
        response = client.post("/api/setup/database")
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data["status"] == "SUCCESS"
        assert data["created_tables"] == "ALREADY EXISTS"

    def test_setup_database_failure_case_not_debug(self, client, monkeypatch):
        """Test failure case: endpoint not available if not in debug mode."""
        monkeypatch.setenv("DEBUG", "false")
        response = client.post("/api/setup/database")
        assert response.status_code == 403
        # Flask abort returns HTML by default, so no JSON expected

    def test_health_check_normal_case(self, client):
        """Test the health check endpoint."""
        # Reason: Verify basic app functionality
        response = client.get("/health")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["app"] == "Tattoo Studio Manager"

    def test_create_user_normal_case(self, client):
        """Test creating a user via API."""
        # Reason: Test normal user creation flow
        user_data = {"name": "John Doe", "birth": 1990, "active": True}

        response = client.post(
            "/api/users", data=json.dumps(user_data), content_type="application/json"
        )
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data["success"] is True
        assert data["user"]["name"] == "John Doe"
        assert data["user"]["birth"] == 1990
        assert "id" in data["user"]

    def test_create_user_edge_case(self, client):
        """Test creating a user with minimal data."""
        # Reason: Test edge case with only required fields
        user_data = {"name": "Jane Smith"}

        response = client.post(
            "/api/users", data=json.dumps(user_data), content_type="application/json"
        )
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data["success"] is True
        assert data["user"]["name"] == "Jane Smith"
        assert data["user"]["birth"] is None
        assert data["user"]["active"] is True

    def test_create_user_failure_case(self, client):
        """Test creating a user with invalid data."""
        # Reason: Test failure case with missing required fields
        user_data = {}

        response = client.post(
            "/api/users", data=json.dumps(user_data), content_type="application/json"
        )
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data["success"] is False
        assert "Name is required" in data["error"]

    def test_get_users_normal_case(self, client):
        """Test retrieving all users."""
        # Create test users first
        client.post(
            "/api/users",
            data=json.dumps({"name": "User 1", "birth": 1990}),
            content_type="application/json",
        )
        client.post(
            "/api/users",
            data=json.dumps({"name": "User 2", "birth": 1991}),
            content_type="application/json",
        )

        response = client.get("/api/users")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["count"] == 2
        assert len(data["users"]) == 2

    def test_get_user_by_id_normal_case(self, client):
        """Test retrieving a specific user by ID."""
        # Create a user first
        create_response = client.post(
            "/api/users",
            data=json.dumps({"name": "Alice Johnson", "birth": 1985}),
            content_type="application/json",
        )
        create_data = json.loads(create_response.data)
        user_id = create_data["user"]["id"]

        # Get the user
        response = client.get(f"/api/users/{user_id}")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["user"]["name"] == "Alice Johnson"
        assert data["user"]["id"] == user_id

    def test_get_user_by_id_edge_case(self, client):
        """Test retrieving a non-existent user."""
        # Reason: Test edge case with non-existent ID
        response = client.get("/api/users/99999")
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data["success"] is False
        assert "User not found" in data["error"]

    def test_update_user_normal_case(self, client):
        """Test updating user information."""
        # Create a user first
        create_response = client.post(
            "/api/users",
            data=json.dumps({"name": "Bob Wilson", "birth": 1988}),
            content_type="application/json",
        )
        create_data = json.loads(create_response.data)
        user_id = create_data["user"]["id"]

        # Update the user
        update_data = {"name": "Robert Wilson", "birth": 1989}
        response = client.put(
            f"/api/users/{user_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["user"]["name"] == "Robert Wilson"
        assert data["user"]["birth"] == 1989

    def test_delete_user_normal_case(self, client):
        """Test deleting a user."""
        # Create a user first
        create_response = client.post(
            "/api/users",
            data=json.dumps({"name": "Charlie Brown", "birth": 1992}),
            content_type="application/json",
        )
        create_data = json.loads(create_response.data)
        user_id = create_data["user"]["id"]

        # Delete the user
        response = client.delete(f"/api/users/{user_id}")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True

        # Verify user is deleted
        get_response = client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 404

    def test_search_user_by_name_normal_case(self, client):
        """Test searching for a user by name."""
        # Create a user first
        client.post(
            "/api/users",
            data=json.dumps({"name": "David Smith", "birth": 1987}),
            content_type="application/json",
        )

        # Search for the user
        response = client.get("/api/users/search?name=David Smith")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["user"]["name"] == "David Smith"

    def test_search_user_failure_case(self, client):
        """Test searching with missing name parameter."""
        # Reason: Test failure case with missing required parameter
        response = client.get("/api/users/search")
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data["success"] is False
        assert "Name parameter is required" in data["error"]

    def test_404_endpoint(self, client):
        """Test 404 error handling."""
        response = client.get("/api/nonexistent")
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data["success"] is False
        assert "Endpoint not found" in data["error"]

    def test_method_not_allowed(self, client):
        """Test 405 error handling."""
        response = client.patch("/api/users")  # PATCH not allowed
        data = json.loads(response.data)

        assert response.status_code == 405
        assert data["success"] is False
        assert "Method not allowed" in data["error"]

    def test_create_users_with_duplicate_names(self, client):
        """Test that users with duplicate names can be created (only ID is unique)."""
        # Reason: Verify duplicate names are allowed, only ID must be unique
        user_data_1 = {"name": "John Smith", "birth": 1990}
        user_data_2 = {"name": "John Smith", "birth": 1985}

        # Create first user
        response1 = client.post(
            "/api/users", data=json.dumps(user_data_1), content_type="application/json"
        )
        data1 = json.loads(response1.data)

        # Create second user with same name
        response2 = client.post(
            "/api/users", data=json.dumps(user_data_2), content_type="application/json"
        )
        data2 = json.loads(response2.data)

        # Both users should be created successfully
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert data1["success"] is True
        assert data2["success"] is True

        # Both should have same name but different IDs and birth years
        assert data1["user"]["name"] == "John Smith"
        assert data2["user"]["name"] == "John Smith"
        assert data1["user"]["id"] != data2["user"]["id"]
        assert data1["user"]["birth"] == 1990
        assert data2["user"]["birth"] == 1985

        # Verify both users exist in the system
        get_response1 = client.get(f"/api/users/{data1['user']['id']}")
        get_response2 = client.get(f"/api/users/{data2['user']['id']}")

        assert get_response1.status_code == 200
        assert get_response2.status_code == 200
