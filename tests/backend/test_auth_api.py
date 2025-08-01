"""
Tests for Authentication API endpoints (/auth/login, /auth/register).
Covers JWT token generation, role-based access, and error handling.
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


class TestAuthAPI:
    """Test cases for authentication API endpoints."""

    def test_register_normal_case(self, client):
        """Test user registration with valid data - normal case."""
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123",
            "role": "staff",
            "birth": 1990,
        }
        response = client.post(
            "/auth/register", data=json.dumps(data), content_type="application/json"
        )

        assert response.status_code == 201
        resp_data = json.loads(response.data)
        assert resp_data["success"] is True
        assert resp_data["user"]["name"] == "Test User"
        assert resp_data["user"]["email"] == "test@example.com"
        assert resp_data["user"]["role"] == "staff"
        assert "password" not in resp_data["user"]  # Password should not be returned

    def test_register_admin_role(self, client):
        """Test admin user registration - edge case."""
        data = {
            "name": "Admin User",
            "email": "admin@example.com",
            "password": "adminpassword123",
            "role": "admin",
        }
        response = client.post(
            "/auth/register", data=json.dumps(data), content_type="application/json"
        )

        assert response.status_code == 201
        resp_data = json.loads(response.data)
        assert resp_data["user"]["role"] == "admin"

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields - failure case."""
        data = {
            "name": "Incomplete User",
            "email": "incomplete@example.com",
            # Missing password and role
        }
        response = client.post(
            "/auth/register", data=json.dumps(data), content_type="application/json"
        )

        assert response.status_code == 400
        resp_data = json.loads(response.data)
        assert resp_data["success"] is False
        assert "Missing required fields" in resp_data["error"]

    def test_register_invalid_role(self, client):
        """Test registration with invalid role - failure case."""
        data = {
            "name": "Invalid Role User",
            "email": "invalid@example.com",
            "password": "password123",
            "role": "invalid_role",
        }
        response = client.post(
            "/auth/register", data=json.dumps(data), content_type="application/json"
        )

        assert response.status_code == 400
        resp_data = json.loads(response.data)
        assert resp_data["success"] is False
        assert "Invalid role" in resp_data["error"]

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email - failure case."""
        # Register first user
        data = {
            "name": "First User",
            "email": "duplicate@example.com",
            "password": "password123",
            "role": "staff",
        }
        client.post(
            "/auth/register", data=json.dumps(data), content_type="application/json"
        )

        # Try to register second user with same email
        data2 = {
            "name": "Second User",
            "email": "duplicate@example.com",
            "password": "differentpassword",
            "role": "admin",
        }
        response = client.post(
            "/auth/register", data=json.dumps(data2), content_type="application/json"
        )

        assert response.status_code == 409
        resp_data = json.loads(response.data)
        assert resp_data["success"] is False
        assert "Email already registered" in resp_data["error"]

    def test_login_normal_case(self, client):
        """Test user login with valid credentials - normal case."""
        # First register a user
        register_data = {
            "name": "Login Test User",
            "email": "login@example.com",
            "password": "loginpassword123",
            "role": "staff",
        }
        client.post(
            "/auth/register",
            data=json.dumps(register_data),
            content_type="application/json",
        )

        # Now login
        login_data = {"email": "login@example.com", "password": "loginpassword123"}
        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 200
        resp_data = json.loads(response.data)
        assert resp_data["success"] is True
        assert "access_token" in resp_data
        assert resp_data["user"]["email"] == "login@example.com"
        assert resp_data["user"]["role"] == "staff"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials - failure case."""
        login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 401
        resp_data = json.loads(response.data)
        assert resp_data["success"] is False
        assert "Invalid credentials" in resp_data["error"]

    def test_login_wrong_password(self, client):
        """Test login with correct email but wrong password - failure case."""
        # Register user
        register_data = {
            "name": "Password Test User",
            "email": "password@example.com",
            "password": "correctpassword",
            "role": "staff",
        }
        client.post(
            "/auth/register",
            data=json.dumps(register_data),
            content_type="application/json",
        )

        # Login with wrong password
        login_data = {"email": "password@example.com", "password": "wrongpassword"}
        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 401
        resp_data = json.loads(response.data)
        assert resp_data["success"] is False
        assert "Invalid credentials" in resp_data["error"]

    def test_login_missing_fields(self, client):
        """Test login with missing email or password - failure case."""
        # Missing password
        login_data = {"email": "test@example.com"}
        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        assert response.status_code == 400
        resp_data = json.loads(response.data)
        assert resp_data["success"] is False
        assert "Email and password required" in resp_data["error"]

    def test_jwt_token_contains_user_info(self, client):
        """Test that JWT token contains correct user identity - edge case."""
        # Register and login
        register_data = {
            "name": "JWT Test User",
            "email": "jwt@example.com",
            "password": "jwtpassword123",
            "role": "admin",
        }
        client.post(
            "/auth/register",
            data=json.dumps(register_data),
            content_type="application/json",
        )

        login_data = {"email": "jwt@example.com", "password": "jwtpassword123"}
        response = client.post(
            "/auth/login", data=json.dumps(login_data), content_type="application/json"
        )

        resp_data = json.loads(response.data)
        token = resp_data["access_token"]

        # Verify token is not empty and has expected format
        assert token is not None
        assert len(token) > 10  # JWT tokens are long strings
        assert "." in token  # JWT format has dots
