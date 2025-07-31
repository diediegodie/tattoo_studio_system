"""
Tests for Session API endpoints (CRUD).
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch
from backend.app_factory import create_app
from services.database_initializer import initialize_database


@pytest.fixture
def client(isolated_test_session, test_engine):
    """Create a test client for the Flask app with proper database setup."""
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

            # Initialize database with test engine
            initialize_database(engine=test_engine, session=isolated_test_session)

            try:
                yield client
            finally:
                # Restore original database connections
                base.db = original_db
                base.session = original_session


def test_create_session_normal_case(client):
    """Test creating a session with all fields."""
    # Create client and artist first
    client_resp = client.post(
        "/api/clients/",
        data=json.dumps({"name": "Client1"}),
        content_type="application/json",
    )
    client_id = json.loads(client_resp.data)["client"]["id"]
    artist_resp = client.post(
        "/api/artists/",
        data=json.dumps({"name": "Artist1"}),
        content_type="application/json",
    )
    artist_id = json.loads(artist_resp.data)["artist"]["id"]
    date_str = (datetime.now() + timedelta(days=1)).isoformat()
    data = {
        "client_id": client_id,
        "artist_id": artist_id,
        "date": date_str,
        "status": "planned",
        "notes": "First session",
    }
    response = client.post(
        "/api/sessions/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 201
    resp_data = json.loads(response.data)
    assert resp_data["session"]["client_id"] == client_id
    assert resp_data["session"]["artist_id"] == artist_id
    assert resp_data["session"]["status"] == "planned"


def test_create_session_edge_case(client):
    """Test creating a session with only required fields."""
    client_resp = client.post(
        "/api/clients/",
        data=json.dumps({"name": "Client2"}),
        content_type="application/json",
    )
    client_id = json.loads(client_resp.data)["client"]["id"]
    artist_resp = client.post(
        "/api/artists/",
        data=json.dumps({"name": "Artist2"}),
        content_type="application/json",
    )
    artist_id = json.loads(artist_resp.data)["artist"]["id"]
    date_str = (datetime.now() + timedelta(days=2)).isoformat()
    data = {"client_id": client_id, "artist_id": artist_id, "date": date_str}
    response = client.post(
        "/api/sessions/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 201
    resp_data = json.loads(response.data)
    assert resp_data["session"]["client_id"] == client_id
    assert resp_data["session"]["artist_id"] == artist_id


def test_create_session_failure_case(client):
    """Test creating a session with missing date (should fail)."""
    client_resp = client.post(
        "/api/clients/",
        data=json.dumps({"name": "Client3"}),
        content_type="application/json",
    )
    client_id = json.loads(client_resp.data)["client"]["id"]
    artist_resp = client.post(
        "/api/artists/",
        data=json.dumps({"name": "Artist3"}),
        content_type="application/json",
    )
    artist_id = json.loads(artist_resp.data)["artist"]["id"]
    data = {"client_id": client_id, "artist_id": artist_id}
    response = client.post(
        "/api/sessions/", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 400


def test_get_session_normal_case(client):
    """Test retrieving a session by ID."""
    client_resp = client.post(
        "/api/clients/",
        data=json.dumps({"name": "Client4"}),
        content_type="application/json",
    )
    client_id = json.loads(client_resp.data)["client"]["id"]
    artist_resp = client.post(
        "/api/artists/",
        data=json.dumps({"name": "Artist4"}),
        content_type="application/json",
    )
    artist_id = json.loads(artist_resp.data)["artist"]["id"]
    date_str = (datetime.now() + timedelta(days=3)).isoformat()
    post_resp = client.post(
        "/api/sessions/",
        data=json.dumps(
            {"client_id": client_id, "artist_id": artist_id, "date": date_str}
        ),
        content_type="application/json",
    )
    session_id = json.loads(post_resp.data)["session"]["id"]
    get_resp = client.get(f"/api/sessions/{session_id}")
    assert get_resp.status_code == 200
    resp_data = json.loads(get_resp.data)
    assert resp_data["session"]["id"] == session_id


def test_update_session_normal_case(client):
    """Test updating a session's info."""
    client_resp = client.post(
        "/api/clients/",
        data=json.dumps({"name": "Client5"}),
        content_type="application/json",
    )
    client_id = json.loads(client_resp.data)["client"]["id"]
    artist_resp = client.post(
        "/api/artists/",
        data=json.dumps({"name": "Artist5"}),
        content_type="application/json",
    )
    artist_id = json.loads(artist_resp.data)["artist"]["id"]
    date_str = (datetime.now() + timedelta(days=4)).isoformat()
    post_resp = client.post(
        "/api/sessions/",
        data=json.dumps(
            {"client_id": client_id, "artist_id": artist_id, "date": date_str}
        ),
        content_type="application/json",
    )
    session_id = json.loads(post_resp.data)["session"]["id"]
    update_data = {"status": "completed", "notes": "Session done"}
    put_resp = client.put(
        f"/api/sessions/{session_id}",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert put_resp.status_code == 200
    resp_data = json.loads(put_resp.data)
    assert resp_data["session"]["status"] == "completed"
    assert resp_data["session"]["notes"] == "Session done"


def test_delete_session_normal_case(client):
    """Test deleting a session."""
    client_resp = client.post(
        "/api/clients/",
        data=json.dumps({"name": "Client6"}),
        content_type="application/json",
    )
    client_id = json.loads(client_resp.data)["client"]["id"]
    artist_resp = client.post(
        "/api/artists/",
        data=json.dumps({"name": "Artist6"}),
        content_type="application/json",
    )
    artist_id = json.loads(artist_resp.data)["artist"]["id"]
    date_str = (datetime.now() + timedelta(days=5)).isoformat()
    post_resp = client.post(
        "/api/sessions/",
        data=json.dumps(
            {"client_id": client_id, "artist_id": artist_id, "date": date_str}
        ),
        content_type="application/json",
    )
    session_id = json.loads(post_resp.data)["session"]["id"]
    del_resp = client.delete(f"/api/sessions/{session_id}")
    assert del_resp.status_code == 200
    resp_data = json.loads(del_resp.data)
    assert resp_data["success"] is True


def test_list_all_sessions(client):
    """Test listing all sessions."""
    # Create two sessions
    client_resp = client.post(
        "/api/clients/",
        data=json.dumps({"name": "Client7"}),
        content_type="application/json",
    )
    client_id = json.loads(client_resp.data)["client"]["id"]
    artist_resp = client.post(
        "/api/artists/",
        data=json.dumps({"name": "Artist7"}),
        content_type="application/json",
    )
    artist_id = json.loads(artist_resp.data)["artist"]["id"]
    date_str1 = (datetime.now() + timedelta(days=6)).isoformat()
    date_str2 = (datetime.now() + timedelta(days=7)).isoformat()
    client.post(
        "/api/sessions/",
        data=json.dumps(
            {"client_id": client_id, "artist_id": artist_id, "date": date_str1}
        ),
        content_type="application/json",
    )
    client.post(
        "/api/sessions/",
        data=json.dumps(
            {"client_id": client_id, "artist_id": artist_id, "date": date_str2}
        ),
        content_type="application/json",
    )
    resp = client.get("/api/sessions/")
    assert resp.status_code == 200
    resp_data = json.loads(resp.data)
    assert resp_data["count"] >= 2


def test_get_session_not_found(client):
    """Test getting a non-existent session."""
    resp = client.get("/api/sessions/99999")
    assert resp.status_code == 404


def test_update_session_not_found(client):
    """Test updating a non-existent session."""
    update_data = {"status": "cancelled"}
    resp = client.put(
        "/api/sessions/99999",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert resp.status_code == 404


def test_delete_session_not_found(client):
    """Test deleting a non-existent session."""
    resp = client.delete("/api/sessions/99999")
    assert resp.status_code == 404
