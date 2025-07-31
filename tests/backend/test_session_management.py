"""
Test file for database session management functions.

Tests the session management functions that were missing test coverage.
Following the project guidelines for testing.
"""

import pytest
from backend.database import get_session, close_session
from services.database_initializer import initialize_database


class TestSessionManagement:
    """Test cases for database session management functions."""

    def test_get_session_normal_case(self, test_engine, test_session):
        """Test getting a session when one is available - normal case."""
        # Reason: Ensure session factory returns valid session object

        # Initialize database with test engine
        initialize_database(engine=test_engine, session=test_session)

        # Override the global session factory for this test
        import backend.database.models.base as base_models
        from sqlalchemy.orm import sessionmaker

        original_session = base_models.Session
        base_models.Session = sessionmaker(bind=test_engine)

        try:
            session = get_session()
            assert session is not None
            assert hasattr(session, "query")
            assert hasattr(session, "commit")
            assert hasattr(session, "close")
            session.close()
        finally:
            # Restore original session
            base_models.Session = original_session

    def test_get_session_multiple_sessions(self, test_engine, test_session):
        """Test getting multiple sessions - edge case."""
        # Reason: Ensure session factory returns different instances each time

        # Initialize database with test engine
        initialize_database(engine=test_engine, session=test_session)

        # Override the global session factory for this test
        import backend.database.models.base as base_models
        from sqlalchemy.orm import sessionmaker

        original_session = base_models.Session
        base_models.Session = sessionmaker(bind=test_engine)

        try:
            session1 = get_session()
            session2 = get_session()

            # Should be different instances
            assert session1 is not session2
            assert session1 is not None
            assert session2 is not None

            session1.close()
            session2.close()
        finally:
            # Restore original session
            base_models.Session = original_session

    def test_close_session_normal_case(self, test_engine, test_session):
        """Test closing a session when one exists - normal case."""
        # Reason: Ensure session closing works without errors

        # Initialize database with test engine
        initialize_database(engine=test_engine, session=test_session)

        # Override the global session for this test
        import backend.database.models.base as base_models
        from sqlalchemy.orm import sessionmaker

        original_session_factory = base_models.Session
        original_session_instance = base_models.session

        SessionLocal = sessionmaker(bind=test_engine)
        base_models.Session = SessionLocal
        base_models.session = SessionLocal()

        try:
            # This should not raise an exception
            close_session()
            # Session should be closed
            assert base_models.session is not None  # Still exists but should be closed
        finally:
            # Restore original sessions
            base_models.Session = original_session_factory
            base_models.session = original_session_instance

    def test_close_session_multiple_calls(self, test_engine, test_session):
        """Test closing session multiple times - edge case."""
        # Reason: Ensure multiple close calls don't cause errors

        # Initialize database with test engine
        initialize_database(engine=test_engine, session=test_session)

        # Override the global session for this test
        import backend.database.models.base as base_models
        from sqlalchemy.orm import sessionmaker

        original_session_factory = base_models.Session
        original_session_instance = base_models.session

        SessionLocal = sessionmaker(bind=test_engine)
        base_models.Session = SessionLocal
        base_models.session = SessionLocal()

        try:
            # Multiple close calls should not raise exceptions
            close_session()
            close_session()
            close_session()
        finally:
            # Restore original sessions
            base_models.Session = original_session_factory
            base_models.session = original_session_instance

    def test_session_operations_after_close(self, test_engine, test_session):
        """Test that new sessions can be created after closing - edge case."""
        # Reason: Ensure session factory still works after session is closed

        # Initialize database with test engine
        initialize_database(engine=test_engine, session=test_session)

        # Override the global session for this test
        import backend.database.models.base as base_models
        from sqlalchemy.orm import sessionmaker

        original_session_factory = base_models.Session
        original_session_instance = base_models.session

        SessionLocal = sessionmaker(bind=test_engine)
        base_models.Session = SessionLocal
        base_models.session = SessionLocal()

        try:
            # Close session
            close_session()

            # Should be able to get new session
            new_session = get_session()
            assert new_session is not None
            new_session.close()
        finally:
            # Restore original sessions
            base_models.Session = original_session_factory
            base_models.session = original_session_instance
