"""
Test file for Artist and Session database models.

This tests the basic CRUD operations for Artist and Session models.
Following the project guidelines for testing and using centralized fixtures.
"""

import pytest
from datetime import datetime
from backend.database.models.base import Base
from backend.database import (
    create_artist,
    read_artist,
    update_artist,
    delete_artist,
    list_all_artists,
    create_session,
    read_session,
    update_session,
    delete_session,
    list_all_sessions,
    create_client,
)


class TestArtistModel:
    """Test cases for Artist model and CRUD operations."""

    def test_create_artist_normal_case(self, test_session):
        """Test creating an artist with normal parameters."""
        artist = create_artist(
            "Bob Wilson", email="bob.wilson@example.com", bio="Tattoo artist"
        )

        assert artist is not None
        assert getattr(artist, "name", None) == "Bob Wilson"
        assert getattr(artist, "email", None) == "bob.wilson@example.com"
        assert getattr(artist, "bio", None) == "Tattoo artist"
        assert getattr(artist, "id", None) is not None

    def test_create_artist_edge_case(self, test_session):
        """Test creating an artist with minimal data."""
        artist = create_artist("Charlie Brown")

        assert artist is not None
        assert getattr(artist, "name", None) == "Charlie Brown"
        assert getattr(artist, "email", None) is None
        assert getattr(artist, "bio", None) is None

    def test_create_artist_failure_case(self, test_session):
        """Test creating an artist with invalid data."""
        with pytest.raises(Exception):
            create_artist(None)  # Name is required

    def test_read_artist_normal_case(self, test_session):
        """Test reading an existing artist."""
        created_artist = create_artist("Alice Artist", email="alice@example.com")
        read_artist_result = read_artist(created_artist.id)

        assert read_artist_result is not None
        assert getattr(read_artist_result, "name", None) == "Alice Artist"
        assert getattr(read_artist_result, "email", None) == "alice@example.com"

    def test_read_artist_edge_case(self, test_session):
        """Test reading a non-existent artist."""
        result = read_artist(99999)
        assert result is None

    def test_update_artist_normal_case(self, test_session):
        """Test updating artist information."""
        artist = create_artist("Update Artist", email="update@example.com")
        updated = update_artist(
            artist.id,
            name="Updated Artist",
            email="updated@example.com",
            bio="Updated bio",
        )

        assert updated is not None
        assert getattr(updated, "name", None) == "Updated Artist"
        assert getattr(updated, "email", None) == "updated@example.com"
        assert getattr(updated, "bio", None) == "Updated bio"

    def test_update_artist_edge_case(self, test_session):
        """Test updating artist with no changes."""
        artist = create_artist("No Change Artist")
        updated = update_artist(artist.id)

        assert updated is not None
        assert getattr(updated, "name", None) == "No Change Artist"

    def test_update_artist_failure_case(self, test_session):
        """Test updating non-existent artist."""
        result = update_artist(99999, name="Ghost Artist")
        assert result is None

    def test_delete_artist_normal_case(self, test_session):
        """Test deleting an artist."""
        artist = create_artist("Delete Artist")
        deleted = delete_artist(artist.id)
        assert deleted is True

        # Verify artist is deleted
        deleted_artist = read_artist(artist.id)
        assert deleted_artist is None

    def test_delete_artist_edge_case(self, test_session):
        """Test deleting non-existent artist."""
        result = delete_artist(99999)
        assert result is False

    def test_list_all_artists_normal_case(self, test_session):
        """Test listing all artists."""
        create_artist("Artist1")
        create_artist("Artist2")
        artists = list_all_artists()

        assert isinstance(artists, list)
        assert len(artists) >= 2

    def test_artist_model_repr(self, test_session):
        """Test the Artist model string representation."""
        artist = create_artist("Test Artist", email="test@example.com")
        repr_str = repr(artist)

        assert "Test Artist" in repr_str
        assert str(artist.id) in repr_str


class TestSessionModel:
    """Test cases for Session model and CRUD operations."""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, test_session):
        """Create test client and artist for session tests."""
        self.test_client = create_client("Test Client")
        self.test_artist = create_artist("Test Artist")

    def test_create_session_normal_case(self, test_session):
        """Test creating a session with normal parameters."""
        session_date = datetime(2025, 8, 1, 10, 0)
        session_obj = create_session(
            self.test_client.id,
            self.test_artist.id,
            session_date,
            status="planned",
            notes="Initial consultation",
        )

        assert session_obj is not None
        assert getattr(session_obj, "client_id", None) == self.test_client.id
        assert getattr(session_obj, "artist_id", None) == self.test_artist.id
        assert getattr(session_obj, "status", None) == "planned"
        assert getattr(session_obj, "notes", None) == "Initial consultation"
        assert getattr(session_obj, "id", None) is not None

    def test_create_session_edge_case(self, test_session):
        """Test creating a session with minimal data."""
        session_date = datetime(2025, 8, 2, 14, 0)
        session_obj = create_session(
            self.test_client.id, self.test_artist.id, session_date
        )

        assert session_obj is not None
        assert getattr(session_obj, "client_id", None) == self.test_client.id
        assert getattr(session_obj, "artist_id", None) == self.test_artist.id
        assert getattr(session_obj, "status", None) == "planned"  # Default status
        assert getattr(session_obj, "notes", None) is None

    def test_create_session_failure_case(self, test_session):
        """Test creating a session with invalid data."""
        with pytest.raises(Exception):
            create_session(None, None, None)  # Required fields missing

    def test_read_session_normal_case(self, test_session):
        """Test reading an existing session."""
        session_date = datetime(2025, 8, 3, 16, 0)
        created_session = create_session(
            self.test_client.id, self.test_artist.id, session_date, notes="Test session"
        )
        read_session_result = read_session(created_session.id)

        assert read_session_result is not None
        assert getattr(read_session_result, "client_id", None) == self.test_client.id
        assert getattr(read_session_result, "artist_id", None) == self.test_artist.id
        assert getattr(read_session_result, "notes", None) == "Test session"

    def test_read_session_edge_case(self, test_session):
        """Test reading a non-existent session."""
        result = read_session(99999)
        assert result is None

    def test_update_session_normal_case(self, test_session):
        """Test updating session information."""
        session_date = datetime(2025, 8, 4, 11, 0)
        session_obj = create_session(
            self.test_client.id, self.test_artist.id, session_date, status="planned"
        )
        updated = update_session(
            session_obj.id, status="completed", notes="Session completed successfully"
        )

        assert updated is not None
        assert getattr(updated, "status", None) == "completed"
        assert getattr(updated, "notes", None) == "Session completed successfully"

    def test_update_session_edge_case(self, test_session):
        """Test updating session with no changes."""
        session_date = datetime(2025, 8, 5, 9, 0)
        session_obj = create_session(
            self.test_client.id, self.test_artist.id, session_date
        )
        updated = update_session(session_obj.id)

        assert updated is not None
        assert getattr(updated, "status", None) == "planned"  # Should remain unchanged

    def test_update_session_failure_case(self, test_session):
        """Test updating non-existent session."""
        result = update_session(99999, status="ghost")
        assert result is None

    def test_delete_session_normal_case(self, test_session):
        """Test deleting a session."""
        session_date = datetime(2025, 8, 6, 13, 0)
        session_obj = create_session(
            self.test_client.id, self.test_artist.id, session_date
        )
        deleted = delete_session(session_obj.id)
        assert deleted is True

        # Verify session is deleted
        deleted_session = read_session(session_obj.id)
        assert deleted_session is None

    def test_delete_session_edge_case(self, test_session):
        """Test deleting non-existent session."""
        result = delete_session(99999)
        assert result is False

    def test_list_all_sessions_normal_case(self, test_session):
        """Test listing all sessions."""
        session_date1 = datetime(2025, 8, 7, 10, 0)
        session_date2 = datetime(2025, 8, 8, 15, 0)

        create_session(self.test_client.id, self.test_artist.id, session_date1)
        create_session(self.test_client.id, self.test_artist.id, session_date2)
        sessions = list_all_sessions()

        assert isinstance(sessions, list)
        assert len(sessions) >= 2

    def test_session_model_repr(self, test_session):
        """Test the Session model string representation."""
        session_date = datetime(2025, 8, 9, 12, 0)
        session_obj = create_session(
            self.test_client.id, self.test_artist.id, session_date, notes="Test repr"
        )
        repr_str = repr(session_obj)

        assert str(session_obj.id) in repr_str
        assert (
            str(self.test_client.id) in repr_str or str(self.test_artist.id) in repr_str
        )
