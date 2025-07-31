"""
Test file for database models.

This tests the basic CRUD operations for the User model.
Following the project guidelines for testing.
"""

import pytest
import os
import tempfile
from backend.database.models import (
    User,
    initialize_database,
    create_user,
    read_user,
    read_user_by_name,
    update_user,
    delete_user,
    list_all_users,
)


class TestUserModel:
    """Test cases for User model and CRUD operations."""

    def setup_method(self):
        """Set up test database before each test."""
        # Create a temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()

        # Override database path for testing
        import backend.database.models as models

        self.original_db_path = models.DB_PATH
        models.DB_PATH = self.temp_db.name

        # Recreate engine and session with new path
        models.db = models.create_engine(f"sqlite:///{self.temp_db.name}", echo=False)
        models.Session = models.sessionmaker(bind=models.db)
        models.session = models.Session()

        # Initialize database
        initialize_database()

    def teardown_method(self):
        """Clean up after each test."""
        # Close session and restore original database path
        import backend.database.models as models

        models.session.close()
        models.DB_PATH = self.original_db_path

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
        assert getattr(user1, "name", None) == getattr(user2, "name", None) == "John Smith"
        assert getattr(user1, "id", None) != getattr(user2, "id", None)  # IDs must be different
        assert getattr(user1, "birth", None) != getattr(user2, "birth", None)  # Different birth years

        # Verify both users exist in database
        retrieved_user1 = read_user(getattr(user1, "id", None))
        retrieved_user2 = read_user(getattr(user2, "id", None))

        assert getattr(retrieved_user1, "name", None) == "John Smith"
        assert getattr(retrieved_user2, "name", None) == "John Smith"
        assert getattr(retrieved_user1, "id", None) != getattr(retrieved_user2, "id", None)
