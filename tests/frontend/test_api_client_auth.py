"""
Test APIClient authentication methods (login, register) for normal, edge, and failure cases.
"""

import pytest
from frontend.utils.api_client import APIClient


@pytest.fixture
def api_client():
    # Use a test server or mock server if available; here, use default base_url
    return APIClient(base_url="http://127.0.0.1:5000")


def test_register_and_login_normal_case(api_client):
    """Normal case: Register and login with valid credentials."""
    import random

    email = f"testuser_{random.randint(1000,9999)}@example.com"
    password = "testpassword123"
    name = "Test User"
    # Register
    success, resp = api_client.register(
        email=email, password=password, name=name, role="staff"
    )
    assert success, f"Register failed: {resp}"
    assert resp.get("user", {}).get("email") == email
    # Login
    success, resp = api_client.login(email=email, password=password)
    assert success, f"Login failed: {resp}"
    assert "access_token" in resp
    # Reason: Refactored attribute name in APIClient
    assert api_client.jwt_token is not None


def test_login_invalid_credentials(api_client):
    """Failure case: Login with invalid credentials should fail."""
    success, resp = api_client.login(email="notfound@example.com", password="wrongpass")
    assert not success
    assert "error" in resp
    assert "Invalid credentials" in resp["error"] or resp.get("status_code") == 401


def test_register_missing_fields(api_client):
    """Edge case: Register with missing fields should fail."""
    success, resp = api_client.register(email="", password="", name="", role="staff")
    assert not success
    assert "error" in resp
    # Reason: API response does not include status_code, check error and success fields
    assert resp.get("success") is False
    assert "Missing required fields" in resp.get("error", "")
