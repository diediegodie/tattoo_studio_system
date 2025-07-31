"""
Test file for database models.

This tests the basic CRUD operations for the User model.
Following the project guidelines for testing.
"""

import pytest
import os
import tempfile
from datetime import datetime
from backend.database import (
    User,
    Client,
    Artist,
    Session,
    initialize_database,
    create_user,
    read_user,
    read_user_by_name,
    update_user,
    delete_user,
    list_all_users,
    create_client,
    read_client,
    update_client,
    delete_client,
    list_all_clients,
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
)


class TestUserModel:
    """Test cases for User model and CRUD operations."""

    def setup_method(self):
        """Set up test database before each test."""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()

        # Override database path for testing
        import backend.database.models.base as base_models

        self.original_db_path = base_models.DB_PATH
        base_models.DB_PATH = self.temp_db.name

        # Recreate engine and session with new path
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        base_models.db = create_engine(f"sqlite:///{self.temp_db.name}", echo=False)
        base_models.Session = sessionmaker(bind=base_models.db)
        base_models.session = base_models.Session()

        # Update the session in all model modules
        from backend.database.models import (
            user_model,
            client_model,
            artist_model,
            session_model,
        )

        user_model.session = base_models.session
        client_model.session = base_models.session
        artist_model.session = base_models.session
        session_model.session = base_models.session

        # Initialize database - ensure all models are imported first
        # This imports the models so their metadata is registered with Base
        from backend.database.models.user_model import User
        from backend.database.models.client_model import Client
        from backend.database.models.artist_model import Artist
        from backend.database.models.session_model import Session

        # Now create the tables
        base_models.Base.metadata.create_all(bind=base_models.db)

    def teardown_method(self):
        """Clean up after each test."""
        # Close session and restore original database path
        import backend.database.models.base as base_models

        base_models.session.close()
        base_models.DB_PATH = self.original_db_path

        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_create_user_normal_case(self):
        """Test creating a user with normal parameters."""
        # Reason: Test normal user creation flow
        user = create_user("John Doe", birth=1990)

        assert user is not None
        assert getattr(user, "name", None) == "John Doe"
        assert getattr(user, "birth", None) == 1990
        assert getattr(user, "active", None) is True
        assert getattr(user, "id", None) is not None

    def test_create_user_edge_case(self):
        """Test creating a user with minimal data."""
        # Reason: Test edge case with only required fields
        user = create_user("Jane Smith")

        assert user is not None
        assert getattr(user, "name", None) == "Jane Smith"
        assert getattr(user, "birth", None) is None
        assert getattr(user, "active", None) is True

    def test_create_user_failure_case(self):
        """Test creating a user with invalid data."""
        # Reason: Test failure case with invalid parameters
        with pytest.raises(Exception):
            create_user(None)  # Name is required

    def test_read_user_normal_case(self):
        """Test reading an existing user."""
        # Create a user first
        created_user = create_user("Alice Johnson", birth=1985)

        # Read the user back
        read_user_result = read_user(created_user.id)

        assert read_user_result is not None
        assert getattr(read_user_result, "name", None) == "Alice Johnson"
        assert getattr(read_user_result, "birth", None) == 1985

    def test_read_user_edge_case(self):
        """Test reading a non-existent user."""
        # Reason: Test edge case with non-existent ID
        result = read_user(99999)
        assert result is None

    def test_read_user_by_name_normal_case(self):
        """Test reading user by name."""
        # Create a user first
        create_user("Bob Wilson", birth=1988)

        # Read by name
        result = read_user_by_name("Bob Wilson")

        assert result is not None
        assert getattr(result, "name", None) == "Bob Wilson"
        assert getattr(result, "birth", None) == 1988

    def test_update_user_normal_case(self):
        """Test updating user information."""
        # Create a user first
        user = create_user("Charlie Brown", birth=1992)

        # Update the user
        updated_user = update_user(user.id, name="Charles Brown", birth=1993)

        assert updated_user is not None
        assert getattr(updated_user, "name", None) == "Charles Brown"
        assert getattr(updated_user, "birth", None) == 1993

    def test_update_user_edge_case(self):
        """Test updating non-existent user."""
        # Reason: Test edge case with invalid user ID
        result = update_user(99999, name="Ghost User")
        assert result is None

    def test_delete_user_normal_case(self):
        """Test deleting an existing user."""
        # Create a user first
        user = create_user("David Smith", birth=1987)

        # Delete the user
        result = delete_user(user.id)

        assert result is True

        # Verify user is deleted
        deleted_user = read_user(user.id)
        assert deleted_user is None

    def test_delete_user_failure_case(self):
        """Test deleting a non-existent user."""
        # Reason: Test failure case with invalid user ID
        result = delete_user(99999)
        assert result is False

    def test_list_all_users_normal_case(self):
        """Test listing all users."""
        # Create multiple users
        create_user("User 1", birth=1990)
        create_user("User 2", birth=1991)
        create_user("User 3", birth=1992, active=False)

        # List only active users
        active_users = list_all_users(active_only=True)
        assert len(active_users) == 2

        # List all users
        all_users = list_all_users(active_only=False)
        assert len(all_users) == 3

    def test_user_model_repr(self):
        """Test the User model string representation."""
        user = create_user("Test User", birth=1995)
        repr_str = repr(user)

        assert "Test User" in repr_str
        assert "1995" in repr_str
        assert str(user.id) in repr_str

    def test_create_duplicate_names_allowed(self):
        """Test that users with duplicate names can be created (only ID is unique)."""
        # Reason: Verify that duplicate names are allowed in the system
        user1 = create_user("John Smith", birth=1990)
        user2 = create_user("John Smith", birth=1985)  # Same name, different birth year

        assert user1 is not None
        assert user2 is not None
        assert (
            getattr(user1, "name", None) == getattr(user2, "name", None) == "John Smith"
        )
        assert getattr(user1, "id", None) != getattr(
            user2, "id", None
        )  # IDs must be different
        assert getattr(user1, "birth", None) != getattr(
            user2, "birth", None
        )  # Different birth years

        # Verify both users exist in database
        retrieved_user1 = read_user(getattr(user1, "id", None))
        retrieved_user2 = read_user(getattr(user2, "id", None))

        assert getattr(retrieved_user1, "name", None) == "John Smith"
        assert getattr(retrieved_user2, "name", None) == "John Smith"
        assert getattr(retrieved_user1, "id", None) != getattr(
            retrieved_user2, "id", None
        )


class TestClientModel:
    """Test cases for Client model and CRUD operations."""

    def setup_method(self):
        """Set up test database before each test."""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()

        # Override database path for testing
        import backend.database.models.base as base_models

        self.original_db_path = base_models.DB_PATH
        base_models.DB_PATH = self.temp_db.name

        # Create new engine and session for test database
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Update engine and session in base module
        base_models.db = create_engine(f"sqlite:///{self.temp_db.name}", echo=False)
        base_models.Session = sessionmaker(bind=base_models.db)
        base_models.session = base_models.Session()

        # Update the session in all model modules
        from backend.database.models import (
            user_model,
            client_model,
            artist_model,
            session_model,
        )

        user_model.session = base_models.session
        client_model.session = base_models.session
        artist_model.session = base_models.session
        session_model.session = base_models.session

        # Create all tables
        base_models.Base.metadata.create_all(base_models.db)

    def teardown_method(self):
        """Clean up after each test."""
        import backend.database.models.base as base_models

        base_models.session.close()
        base_models.DB_PATH = self.original_db_path

        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_create_client_normal_case(self):
        """Test creating a client with normal parameters."""
        client = create_client("John Doe", phone="123-456-7890", address="123 Main St")

        assert client is not None
        assert getattr(client, "name", None) == "John Doe"
        assert getattr(client, "phone", None) == "123-456-7890"
        assert getattr(client, "address", None) == "123 Main St"
        assert getattr(client, "id", None) is not None

    def test_create_client_edge_case(self):
        """Test creating a client with minimal data."""
        client = create_client("Jane Smith")

        assert client is not None
        assert getattr(client, "name", None) == "Jane Smith"
        assert getattr(client, "phone", None) is None

    def test_create_client_failure_case(self):
        """Test creating a client with invalid data."""
        with pytest.raises(Exception):
            create_client(None)

    def test_read_client_normal_case(self):
        """Test reading an existing client."""
        created_client = create_client("Alice Johnson", phone="555-0123")
        read_client_result = read_client(created_client.id)

        assert read_client_result is not None
        assert getattr(read_client_result, "name", None) == "Alice Johnson"
        assert getattr(read_client_result, "phone", None) == "555-0123"


class TestArtistModel:
    """Test cases for Artist model and CRUD operations."""

    def setup_method(self):
        """Set up test database before each test."""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()

        # Override database path for testing
        import backend.database.models.base as base_models

        self.original_db_path = base_models.DB_PATH
        base_models.DB_PATH = self.temp_db.name

        # Create new engine and session for test database
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Update engine and session in base module
        base_models.db = create_engine(f"sqlite:///{self.temp_db.name}", echo=False)
        base_models.Session = sessionmaker(bind=base_models.db)
        base_models.session = base_models.Session()

        # Update the session in all model modules
        from backend.database.models import (
            user_model,
            client_model,
            artist_model,
            session_model,
        )

        user_model.session = base_models.session
        client_model.session = base_models.session
        artist_model.session = base_models.session
        session_model.session = base_models.session

        # Create all tables
        base_models.Base.metadata.create_all(base_models.db)

    def teardown_method(self):
        """Clean up after each test."""
        import backend.database.models.base as base_models

        base_models.session.close()
        base_models.DB_PATH = self.original_db_path

        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_create_artist_normal_case(self):
        """Test creating an artist with normal parameters."""
        artist = create_artist(
            "Bob Wilson", email="bob.wilson@example.com", bio="Tattoo artist"
        )

        assert artist is not None
        assert getattr(artist, "name", None) == "Bob Wilson"
        assert getattr(artist, "email", None) == "bob.wilson@example.com"
        assert getattr(artist, "bio", None) == "Tattoo artist"

    def test_create_artist_edge_case(self):
        """Test creating an artist with minimal data."""
        artist = create_artist("Charlie Brown")

        assert artist is not None
        assert getattr(artist, "name", None) == "Charlie Brown"
        assert getattr(artist, "email", None) is None


class TestSessionModel:
    """Test cases for Session model and CRUD operations."""

    def setup_method(self):
        """Set up test database before each test."""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()

        # Override database path for testing
        import backend.database.models.base as base_models

        self.original_db_path = base_models.DB_PATH
        base_models.DB_PATH = self.temp_db.name

        # Create new engine and session for test database
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Update engine and session in base module
        base_models.db = create_engine(f"sqlite:///{self.temp_db.name}", echo=False)
        base_models.Session = sessionmaker(bind=base_models.db)
        base_models.session = base_models.Session()

        # Update the session in all model modules
        from backend.database.models import (
            user_model,
            client_model,
            artist_model,
            session_model,
        )

        user_model.session = base_models.session
        client_model.session = base_models.session
        artist_model.session = base_models.session
        session_model.session = base_models.session

        # Create all tables
        base_models.Base.metadata.create_all(base_models.db)

        # Create test client and artist for session tests
        self.test_client = create_client("Test Client")
        self.test_artist = create_artist("Test Artist")

    def teardown_method(self):
        """Clean up after each test."""
        import backend.database.models.base as base_models

        base_models.session.close()
        base_models.DB_PATH = self.original_db_path

        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_create_session_normal_case(self):
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
