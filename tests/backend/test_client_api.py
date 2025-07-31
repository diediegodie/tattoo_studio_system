"""
Tests for Client API endpoints (CRUD).
"""

import pytest
import json
from backend.app_factory import create_app
from backend.database.models.base import Base


@pytest.fixture
def client(isolated_test_session, test_engine):
    """Create a test client for the Flask app with proper database setup."""
    Base.metadata.create_all(bind=test_engine)
    app = create_app()
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_create_client_normal_case(client):
    """Test creating a client with all fields."""
    data = {
        "name": "Alice Smith",
        "phone": "123456789",
        "address": "123 Main St",
        "allergies": "None",
        "medical_info": "Healthy",
        "qr_id": "alice-qr-001",
    }
    response = client.post(
        "/api/clients/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 201
    resp_data = json.loads(response.data)
    assert resp_data["client"]["name"] == "Alice Smith"
    assert resp_data["client"]["qr_id"] == "alice-qr-001"


def test_create_client_edge_case(client):
    """Test creating a client with only required fields."""
    data = {"name": "Bob"}
    response = client.post(
        "/api/clients/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 201
    resp_data = json.loads(response.data)
    assert resp_data["client"]["name"] == "Bob"


def test_create_client_failure_case(client):
    """Test creating a client with missing name (should fail)."""
    data = {"phone": "999"}
    response = client.post(
        "/api/clients/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 400


def test_get_client_normal_case(client):
    """Test retrieving a client by ID."""
    # Create client first
    data = {"name": "Carol"}
    post_resp = client.post(
        "/api/clients/", data=json.dumps(data), content_type="application/json"
    )
    client_id = json.loads(post_resp.data)["client"]["id"]
    get_resp = client.get(f"/api/clients/{client_id}")
    assert get_resp.status_code == 200
    resp_data = json.loads(get_resp.data)
    assert resp_data["client"]["name"] == "Carol"


def test_update_client_normal_case(client):
    """Test updating a client's info."""
    data = {"name": "Dave"}
    post_resp = client.post(
        "/api/clients/", data=json.dumps(data), content_type="application/json"
    )
    client_id = json.loads(post_resp.data)["client"]["id"]
    update_data = {"address": "New Address"}
    put_resp = client.put(
        f"/api/clients/{client_id}",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert put_resp.status_code == 200
    resp_data = json.loads(put_resp.data)
    assert resp_data["client"]["address"] == "New Address"


def test_delete_client_normal_case(client):
    """Test deleting a client."""
    data = {"name": "Eve"}
    post_resp = client.post(
        "/api/clients/", data=json.dumps(data), content_type="application/json"
    )
    client_id = json.loads(post_resp.data)["client"]["id"]
    del_resp = client.delete(f"/api/clients/{client_id}")
    assert del_resp.status_code == 200
    resp_data = json.loads(del_resp.data)
    assert resp_data["success"] is True


def test_list_all_clients(client):
    """Test listing all clients."""
    # Create two clients
    client.post(
        "/api/clients/",
        data=json.dumps({"name": "Frank"}),
        content_type="application/json",
    )
    client.post(
        "/api/clients/",
        data=json.dumps({"name": "Grace"}),
        content_type="application/json",
    )
    resp = client.get("/api/clients/")
    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert resp_data["count"] >= 2


def test_get_client_not_found(client):
    """Test getting a non-existent client."""
    resp = client.get("/api/clients/99999")
    assert resp.status_code == 404


def test_update_client_not_found(client):
    """Test updating a non-existent client."""
    update_data = {"address": "Nowhere"}
    resp = client.put(
        "/api/clients/99999",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert resp.status_code == 404


def test_delete_client_not_found(client):
    """Test deleting a non-existent client."""
    resp = client.delete("/api/clients/99999")
    assert resp.status_code == 404
