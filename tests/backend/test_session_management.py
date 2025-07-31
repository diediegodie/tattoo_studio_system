"""
Test file for database session management functions.

Tests the session management functions that were missing test coverage.
Following the project guidelines for testing.
"""

import pytest
import os
import tempfile
from backend.database.models import get_session, close_session, initialize_database


class TestSessionManagement:
    """Test cases for database session management functions."""

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

        try:
            models.session.close()
        except Exception:
            pass

        # Restore original database path
        models.DB_PATH = self.original_db_path

        # Remove temporary database file
        try:
            os.unlink(self.temp_db.name)
        except OSError:
            pass

    def test_get_session_normal_case(self):
        """Test getting a new database session - normal case."""
        # Reason: Test that get_session returns a valid session object
        session = get_session()

        assert session is not None
        assert hasattr(session, "query")
        assert hasattr(session, "add")
        assert hasattr(session, "commit")
        assert hasattr(session, "close")

    def test_get_session_multiple_sessions(self):
        """Test getting multiple database sessions - edge case."""
        # Reason: Test that multiple sessions can be created independently
        session1 = get_session()
        session2 = get_session()

        assert session1 is not None
        assert session2 is not None
        assert session1 is not session2  # Should be different instances

    def test_close_session_normal_case(self):
        """Test closing database session - normal case."""
        # Reason: Test that close_session executes without errors
        try:
            close_session()
            # If we get here without exception, the test passes
            assert True
        except Exception as e:
            pytest.fail(f"close_session raised an exception: {e}")

    def test_close_session_multiple_calls(self):
        """Test calling close_session multiple times - edge case."""
        # Reason: Test that multiple close calls don't cause errors
        try:
            close_session()
            close_session()  # Should not cause errors
            assert True
        except Exception as e:
            pytest.fail(f"Multiple close_session calls raised an exception: {e}")

    def test_session_operations_after_close(self):
        """Test that operations still work after close_session - failure case."""
        # Reason: Test behavior after session closure
        from backend.database.models import create_user, list_all_users

        # Close the session
        close_session()

        # Operations should still work because they use their own session management
        try:
            user = create_user("Test User After Close", birth=1990)
            assert user is not None
            assert user.name == "Test User After Close"

            users = list_all_users()
            assert len(users) >= 1
        except Exception as e:
            pytest.fail(f"Operations after close_session failed: {e}")
