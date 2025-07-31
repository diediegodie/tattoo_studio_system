import os
import time
import threading
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from frontend.utils.api_client import APIClient
from backend.app_factory import create_app
from backend.database.models.base import Base
from services.database_initializer import initialize_database
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TestFrontendBackendIntegration:
    """
    Integration tests for frontend-backend communication.
    """

    @classmethod
    def setup_class(cls):
        """Set up test environment with Flask app and shared file-based SQLite DB."""
        TEST_DB_URL = "sqlite:///test_integration.db"

        # Remove old test DB if exists
        if os.path.exists("test_integration.db"):
            os.remove("test_integration.db")

        # Create shared engine and tables
        test_engine = create_engine(
            TEST_DB_URL, connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(test_engine)
        initialize_database(engine=test_engine)

        # Patch global references in backend.database.models.base
        import backend.database.models.base as base

        base.db = test_engine
        base.Session = sessionmaker(bind=test_engine)
        base.session = base.Session()

        # Set environment for Flask app
        os.environ["TESTING"] = "1"
        os.environ["DB_URL"] = TEST_DB_URL

        # Create Flask app with test config
        app = create_app({"TESTING": True, "DB_URL": TEST_DB_URL})

        # Start Flask app in test mode in a separate thread
        cls.flask_thread = threading.Thread(
            target=lambda: app.run(
                host="127.0.0.1", port=5000, debug=False, use_reloader=False
            ),
            daemon=True,
        )
        cls.flask_thread.start()

        # Wait for Flask app to start
        time.sleep(2)

        # Initialize API client
        cls.api_client = APIClient(base_url="http://127.0.0.1:5000")

        logger.info("Integration test setup completed")
        app = create_app({"TESTING": True, "DB_URL": TEST_DB_URL})

        # Start Flask app in test mode in a separate thread
        cls.flask_thread = threading.Thread(
            target=lambda: app.run(
                host="127.0.0.1", port=5000, debug=False, use_reloader=False
            ),
            daemon=True,
        )
        cls.flask_thread.start()

        # Wait for Flask app to start
        time.sleep(2)

        # Initialize API client
        cls.api_client = APIClient(base_url="http://127.0.0.1:5000")

        logger.info("Integration test setup completed")

    def test_backend_health_check(self):
        """Test that the backend is healthy and accessible."""
        success, response = self.api_client.health_check()

        assert success, f"Health check failed: {response}"
        assert "status" in response
        assert response["status"] == "healthy"

        logger.info("Backend health check passed")

    def test_user_crud_operations(self):
        """Test complete CRUD operations through API client."""
        # Test 1: Create a new user
        success, response = self.api_client.create_user(
            name="Integration Test User", birth=1990, active=True
        )

        assert success, f"User creation failed: {response}"
        assert "user" in response
        user_id = response["user"]["id"]
        assert response["user"]["name"] == "Integration Test User"
        assert response["user"]["birth"] == 1990
        assert response["user"]["active"] is True

        logger.info(f"Created test user with ID: {user_id}")

        # Test 2: Get the created user
        success, response = self.api_client.get_user(user_id)

        assert success, f"User retrieval failed: {response}"
        assert response["user"]["name"] == "Integration Test User"

        logger.info("User retrieval test passed")

        # Test 3: Update the user
        success, response = self.api_client.update_user(
            user_id, name="Updated Test User", birth=1991, active=False
        )

        assert success, f"User update failed: {response}"
        assert response["user"]["name"] == "Updated Test User"
        assert response["user"]["birth"] == 1991
        assert response["user"]["active"] is False

        logger.info("User update test passed")

        # Test 4: Search for user by name
        success, response = self.api_client.search_user_by_name("Updated Test User")

        assert success, f"User search failed: {response}"
        assert response["user"]["id"] == user_id

        logger.info("User search test passed")

        # Test 5: Get all users (should include our test user)
        success, response = self.api_client.get_all_users(active_only=False)

        assert success, f"Get all users failed: {response}"
        assert "users" in response
        assert len(response["users"]) >= 1

        # Find our test user in the list
        test_user_found = any(user["id"] == user_id for user in response["users"])
        assert test_user_found, "Test user not found in user list"

        logger.info("Get all users test passed")

        # Test 6: Delete the user
        success, response = self.api_client.delete_user(user_id)

        assert success, f"User deletion failed: {response}"

        logger.info("User deletion test passed")

        # Test 7: Verify user is deleted
        success, response = self.api_client.get_user(user_id)

        assert not success, "User should not exist after deletion"
        assert response.get("error") == "User not found"

        logger.info("User deletion verification passed")

    def test_error_handling(self):
        """Test API client error handling for various scenarios."""
        # Test 1: Get non-existent user
        success, response = self.api_client.get_user(99999)

        assert not success
        assert "error" in response

        logger.info("Non-existent user error handling test passed")

        # Test 2: Create user with invalid data
        success, response = self.api_client.create_user(name="")

        assert not success
        assert "error" in response

        logger.info("Invalid user data error handling test passed")

        # Test 3: Update non-existent user
        success, response = self.api_client.update_user(99999, name="Non-existent")

        assert not success
        assert "error" in response

        logger.info("Non-existent user update error handling test passed")

        # Test 4: Search for non-existent user
        success, response = self.api_client.search_user_by_name("Non-existent User")

        assert not success
        assert "error" in response

        logger.info("Non-existent user search error handling test passed")

    def test_connection_resilience(self):
        """Test API client behavior with connection issues."""
        # Create a client with invalid URL
        invalid_client = APIClient(base_url="http://127.0.0.1:9999")

        success, response = invalid_client.health_check()

        assert not success
        assert "error" in response
        assert "connect" in response["error"].lower()

        logger.info("Connection resilience test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
