"""
Tests for Artist API endpoints (CRUD).
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
    app = create_app()
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_create_artist_normal_case(client):
    """Test creating an artist with all fields."""
    data = {
        "name": "Tattoo Joe",
        "phone": "555-1234",
        "email": "joe@ink.com",
        "bio": "Experienced tattoo artist.",
        "portfolio": "http://portfolio.com/joe",
    }
    response = client.post(
        "/api/artists/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 201
    resp_data = json.loads(response.data)
    assert resp_data["artist"]["name"] == "Tattoo Joe"
    assert resp_data["artist"]["email"] == "joe@ink.com"


def test_create_artist_edge_case(client):
    """Test creating an artist with only required fields."""
    data = {"name": "Jane"}
    response = client.post(
        "/api/artists/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 201
    resp_data = json.loads(response.data)
    assert resp_data["artist"]["name"] == "Jane"


def test_create_artist_failure_case(client):
    """Test creating an artist with missing name (should fail)."""
    data = {"email": "fail@ink.com"}
    response = client.post(
        "/api/artists/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 400


def test_get_artist_normal_case(client):
    """Test retrieving an artist by ID."""
    # Create artist first
    data = {"name": "Sam"}
    post_resp = client.post(
        "/api/artists/", data=json.dumps(data), content_type="application/json"
    )
    artist_id = json.loads(post_resp.data)["artist"]["id"]
    get_resp = client.get(f"/api/artists/{artist_id}")
    assert get_resp.status_code == 200
    resp_data = json.loads(get_resp.data)
    assert resp_data["artist"]["name"] == "Sam"


def test_update_artist_normal_case(client):
    """Test updating an artist's info."""
    data = {"name": "Alex"}
    post_resp = client.post(
        "/api/artists/", data=json.dumps(data), content_type="application/json"
    )
    artist_id = json.loads(post_resp.data)["artist"]["id"]
    update_data = {"bio": "Updated bio"}
    put_resp = client.put(
        f"/api/artists/{artist_id}",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert put_resp.status_code == 200
    resp_data = json.loads(put_resp.data)
    assert resp_data["artist"]["bio"] == "Updated bio"


def test_delete_artist_normal_case(client):
    """Test deleting an artist."""
    data = {"name": "Eve"}
    post_resp = client.post(
        "/api/artists/", data=json.dumps(data), content_type="application/json"
    )
    artist_id = json.loads(post_resp.data)["artist"]["id"]
    del_resp = client.delete(f"/api/artists/{artist_id}")
    assert del_resp.status_code == 200
    resp_data = json.loads(del_resp.data)
    assert resp_data["success"] is True


def test_list_all_artists(client):
    """Test listing all artists."""
    # Create two artists
    client.post(
        "/api/artists/",
        data=json.dumps({"name": "Frank"}),
        content_type="application/json",
    )
    client.post(
        "/api/artists/",
        data=json.dumps({"name": "Grace"}),
        content_type="application/json",
    )
    resp = client.get("/api/artists/")
    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert resp_data["count"] >= 2


def test_get_artist_not_found(client):
    """Test getting a non-existent artist."""
    resp = client.get("/api/artists/99999")
    assert resp.status_code == 404


def test_update_artist_not_found(client):
    """Test updating a non-existent artist."""
    update_data = {"bio": "Nowhere"}
    resp = client.put(
        "/api/artists/99999",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert resp.status_code == 404


def test_delete_artist_not_found(client):
    """Test deleting a non-existent artist."""
    resp = client.delete("/api/artists/99999")
    assert resp.status_code == 404
