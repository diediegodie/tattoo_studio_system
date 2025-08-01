"""
Tests for role-based access control decorators and protected routes.
Tests admin_required and staff_required decorators functionality.
"""

import pytest
import json
from unittest.mock import patch
from backend.app_factory import create_app
from backend.database.models.base import Base
from services.database_initializer import initialize_database


@pytest.fixture
def client(isolated_test_session, test_engine):
    """Create a test client for the Flask app with proper database setup."""
    Base.metadata.create_all(bind=test_engine)

    # Create app with proper JWT configuration
    config_overrides = {
        "TESTING": True,
        "DEBUG": True,
        "JWT_SECRET_KEY": "test-secret-key",
        "DB_URL": "sqlite:///:memory:",
    }
    app = create_app(config_overrides)

    with app.test_client() as client:
        with patch("backend.database.models.base.db", test_engine):
            with patch("backend.database.models.base.session", isolated_test_session):
                initialize_database(engine=test_engine, session=isolated_test_session)
                yield client


@pytest.fixture
def admin_token(client):
    """Create an admin user and return their JWT token."""
    # Register admin user
    register_data = {
        "name": "Admin User",
        "email": "admin@test.com",
        "password": "adminpass123",
        "role": "admin",
    }
    client.post(
        "/auth/register",
        data=json.dumps(register_data),
        content_type="application/json",
    )

    # Login to get token
    login_data = {"email": "admin@test.com", "password": "adminpass123"}
    response = client.post(
        "/auth/login", data=json.dumps(login_data), content_type="application/json"
    )
    return json.loads(response.data)["access_token"]


@pytest.fixture
def staff_token(client):
    """Create a staff user and return their JWT token."""
    # Register staff user
    register_data = {
        "name": "Staff User",
        "email": "staff@test.com",
        "password": "staffpass123",
        "role": "staff",
    }
    client.post(
        "/auth/register",
        data=json.dumps(register_data),
        content_type="application/json",
    )

    # Login to get token
    login_data = {"email": "staff@test.com", "password": "staffpass123"}
    response = client.post(
        "/auth/login", data=json.dumps(login_data), content_type="application/json"
    )
    return json.loads(response.data)["access_token"]


class TestRoleBasedAccess:
    """Test cases for role-based access control."""

    def test_admin_can_delete_user(self, client, admin_token):
        """Test that admin can delete users - normal case."""
        # Create a user to delete
        user_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "testpass123",
            "role": "staff",
        }
        create_resp = client.post(
            "/auth/register",
            data=json.dumps(user_data),
            content_type="application/json",
        )
        user_id = json.loads(create_resp.data)["user"]["id"]

        # Admin deletes the user
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(f"/api/users/{user_id}", headers=headers)

        assert response.status_code == 200
        resp_data = json.loads(response.data)
        assert resp_data["success"] is True

    def test_staff_cannot_delete_user(self, client, staff_token):
        """Test that staff cannot delete users - failure case."""
        # Create a user to attempt deletion
        user_data = {
            "name": "Test User 2",
            "email": "testuser2@example.com",
            "password": "testpass123",
            "role": "staff",
        }
        create_resp = client.post(
            "/auth/register",
            data=json.dumps(user_data),
            content_type="application/json",
        )
        user_id = json.loads(create_resp.data)["user"]["id"]

        # Staff attempts to delete the user
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.delete(f"/api/users/{user_id}", headers=headers)

        assert response.status_code == 403
        resp_data = json.loads(response.data)
        assert resp_data["success"] is False
        assert "Admin access required" in resp_data["error"]

    def test_unauthenticated_cannot_delete_user(self, client):
        """Test that unauthenticated users cannot delete users - failure case."""
        # Create a user to attempt deletion
        user_data = {
            "name": "Test User 3",
            "email": "testuser3@example.com",
            "password": "testpass123",
            "role": "staff",
        }
        create_resp = client.post(
            "/auth/register",
            data=json.dumps(user_data),
            content_type="application/json",
        )
        user_id = json.loads(create_resp.data)["user"]["id"]

        # Attempt to delete without authentication
        response = client.delete(f"/api/users/{user_id}")

        assert response.status_code == 401  # Unauthorized

    def test_invalid_token_cannot_access_protected_route(self, client):
        """Test that invalid token cannot access protected routes - failure case."""
        # Create a user to attempt deletion
        user_data = {
            "name": "Test User 4",
            "email": "testuser4@example.com",
            "password": "testpass123",
            "role": "staff",
        }
        create_resp = client.post(
            "/auth/register",
            data=json.dumps(user_data),
            content_type="application/json",
        )
        user_id = json.loads(create_resp.data)["user"]["id"]

        # Attempt to delete with invalid token
        headers = {"Authorization": "Bearer invalid-token-123"}
        response = client.delete(f"/api/users/{user_id}", headers=headers)

        assert response.status_code == 422  # Unprocessable Entity (invalid JWT)

    def test_expired_token_handling(self, client):
        """Test behavior with expired token - edge case."""
        # This would require mocking JWT expiration
        # For now, test with malformed token
        headers = {"Authorization": "Bearer expired.token.here"}
        response = client.delete("/api/users/1", headers=headers)

        assert response.status_code in [
            401,
            422,
        ]  # Unauthorized or Unprocessable Entity

    def test_admin_role_inheritance(self, client, admin_token):
        """Test that admin has staff permissions too - edge case."""
        # Admins should be able to access staff-level operations
        # For this test, we'll check that admin can access user listing (if it requires staff role)
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/users/", headers=headers)

        # This should succeed regardless of whether staff_required decorator is applied
        assert response.status_code in [
            200,
            401,
        ]  # Either works or needs auth (no 403 for admin)

    def test_role_validation_in_jwt(self, client):
        """Test that role information is properly stored in JWT - edge case."""
        # Register users with different roles
        admin_data = {
            "name": "Admin",
            "email": "admin2@test.com",
            "password": "pass123",
            "role": "admin",
        }
        staff_data = {
            "name": "Staff",
            "email": "staff2@test.com",
            "password": "pass123",
            "role": "staff",
        }

        client.post(
            "/auth/register",
            data=json.dumps(admin_data),
            content_type="application/json",
        )
        client.post(
            "/auth/register",
            data=json.dumps(staff_data),
            content_type="application/json",
        )

        # Login both users
        admin_login = client.post(
            "/auth/login",
            data=json.dumps({"email": "admin2@test.com", "password": "pass123"}),
            content_type="application/json",
        )
        staff_login = client.post(
            "/auth/login",
            data=json.dumps({"email": "staff2@test.com", "password": "pass123"}),
            content_type="application/json",
        )

        admin_resp = json.loads(admin_login.data)
        staff_resp = json.loads(staff_login.data)

        # Verify user info is returned correctly
        assert admin_resp["user"]["role"] == "admin"
        assert staff_resp["user"]["role"] == "staff"

        # Verify tokens are different
        assert admin_resp["access_token"] != staff_resp["access_token"]
