"""
Test file for User and Client database models.

This tests the basic CRUD operations for User and Client models.
Following the project guidelines for testing and using centralized fixtures.
"""

import pytest
from backend.database.models.base import Base
from backend.database import (
    create_user,
    read_user,
    read_user_by_name,
    update_user,
    delete_user,
    list_all_users,
    create_client,
    read_client,
)


class TestUserModel:
    """Test cases for User model and CRUD operations."""

    def test_create_user_normal_case(self, test_session):
        """Test creating a user with normal parameters."""
        user = create_user("John Doe", birth=1990)
        assert user is not None
        assert getattr(user, "name", None) == "John Doe"
        assert getattr(user, "birth", None) == 1990
        assert getattr(user, "active", None) is True
        assert getattr(user, "id", None) is not None

    def test_create_user_edge_case(self, test_session):
        """Test creating a user with minimal data."""
        user = create_user("Jane Smith")
        assert user is not None
        assert getattr(user, "name", None) == "Jane Smith"
        assert getattr(user, "birth", None) is None
        assert getattr(user, "active", None) is True

    def test_create_user_failure_case(self, test_session):
        """Test creating a user with invalid data."""
        with pytest.raises(Exception):
            create_user(None)  # Name is required

    def test_read_user_normal_case(self, test_session):
        """Test reading an existing user."""
        created_user = create_user("Alice Johnson", birth=1985)
        read_user_result = read_user(created_user.id)
        assert read_user_result is not None
        assert getattr(read_user_result, "name", None) == "Alice Johnson"
        assert getattr(read_user_result, "birth", None) == 1985

    def test_read_user_edge_case(self, test_session):
        """Test reading a non-existent user."""
        result = read_user(99999)
        assert result is None

    def test_read_user_by_name_normal_case(self, test_session):
        """Test reading user by name."""
        create_user("Bob Wilson", birth=1988)
        result = read_user_by_name("Bob Wilson")
        assert result is not None
        assert getattr(result, "name", None) == "Bob Wilson"
        assert getattr(result, "birth", None) == 1988

    def test_update_user_normal_case(self, test_session):
        """Test updating user information."""
        user = create_user("Update Me", birth=1995)
        updated = update_user(user.id, name="Updated Name", birth=2000)
        assert updated is not None
        assert getattr(updated, "name", None) == "Updated Name"
        assert getattr(updated, "birth", None) == 2000

    def test_update_user_edge_case(self, test_session):
        """Test updating user with no changes."""
        user = create_user("No Change", birth=1992)
        updated = update_user(user.id)
        assert updated is not None
        assert getattr(updated, "name", None) == "No Change"

    def test_update_user_failure_case(self, test_session):
        """Test updating non-existent user."""
        result = update_user(99999, name="Ghost")
        assert result is None

    def test_delete_user_normal_case(self, test_session):
        """Test deleting a user."""
        user = create_user("Delete Me", birth=1980)
        deleted = delete_user(user.id)
        assert deleted is True

    def test_delete_user_edge_case(self, test_session):
        """Test deleting already deleted user."""
        user = create_user("Delete Twice", birth=1981)
        delete_user(user.id)
        deleted_again = delete_user(user.id)
        assert deleted_again is False

    def test_list_all_users_normal_case(self, test_session):
        """Test listing all users."""
        create_user("User1")
        create_user("User2")
        users = list_all_users()
        assert isinstance(users, list)
        assert len(users) >= 2

    def test_user_model_repr(self, test_session):
        """Test the User model string representation."""
        user = create_user("Test User", birth=1995)
        repr_str = repr(user)
        assert "Test User" in repr_str
        assert "1995" in repr_str
        assert str(user.id) in repr_str

    def test_create_duplicate_names_allowed(self, test_session):
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

    def test_list_users_with_active_filter_normal_case(self, isolated_test_session):
        """Test listing users with active filter."""
        # Get initial count
        initial_active_users = list_all_users(active_only=True)
        initial_all_users = list_all_users(active_only=False)
        initial_active_count = len(initial_active_users)
        initial_all_count = len(initial_all_users)

        # Create multiple users with different active status
        create_user("Active User 1", birth=1990)
        create_user("Active User 2", birth=1991)
        create_user("Active User 3", birth=1992, active=False)

        # List only active users
        active_users = list_all_users(active_only=True)
        assert len(active_users) == initial_active_count + 2  # Added 2 active users

        # List all users
        all_users = list_all_users(active_only=False)
        assert len(all_users) == initial_all_count + 3  # Added 3 users total


class TestClientModel:
    """Test cases for Client model and CRUD operations."""

    def test_create_client_normal_case(self, test_session):
        """Test creating a client with normal parameters."""
        client = create_client("John Doe", phone="123-456-7890", address="123 Main St")

        assert client is not None
        assert getattr(client, "name", None) == "John Doe"
        assert getattr(client, "phone", None) == "123-456-7890"
        assert getattr(client, "address", None) == "123 Main St"
        assert getattr(client, "id", None) is not None

    def test_create_client_edge_case(self, test_session):
        """Test creating a client with minimal data."""
        client = create_client("Jane Smith")

        assert client is not None
        assert getattr(client, "name", None) == "Jane Smith"
        assert getattr(client, "phone", None) is None

    def test_create_client_failure_case(self, test_session):
        """Test creating a client with invalid data."""
        with pytest.raises(Exception):
            create_client(None)

    def test_read_client_normal_case(self, test_session):
        """Test reading an existing client."""
        created_client = create_client("Alice Johnson", phone="555-0123")
        read_client_result = read_client(created_client.id)

        assert read_client_result is not None
        assert getattr(read_client_result, "name", None) == "Alice Johnson"
        assert getattr(read_client_result, "phone", None) == "555-0123"

    def test_read_client_edge_case(self, test_session):
        """Test reading a non-existent client."""
        result = read_client(99999)
        assert result is None

    def test_client_model_repr(self, test_session):
        """Test the Client model string representation."""
        client = create_client("Test Client", phone="555-1234")
        repr_str = repr(client)
        assert "Test Client" in repr_str
        assert str(client.id) in repr_str
