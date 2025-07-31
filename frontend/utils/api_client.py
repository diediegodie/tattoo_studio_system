"""
API Client for Tattoo Studio Management System Frontend.

This module provides a centralized API client for making HTTP requests
to the Flask backend. Handles error responses, JSON parsing, and provides
typed responses for better frontend integration.

Key Features:
- Centralized error handling
- JSON request/response handling
- Timeout configuration
- Connection validation
- User-friendly error messages for UI display
"""

import requests
from typing import Dict, List, Optional, Any, Tuple
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from utils.logger import setup_logger
from configs.config import AppConfig

# Initialize logger and config
logger = setup_logger(__name__)
config = AppConfig()


class APIClient:
    """
    HTTP client for communicating with the Flask backend API.

    Provides methods for all user management operations and handles
    error responses appropriately for display in the Flet UI.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """
        Initialize API client.

        Args:
            base_url (str): Base URL of the Flask backend API
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 10  # seconds
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

        logger.info(f"API Client initialized with base URL: {self.base_url}")

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Make an HTTP request and handle common errors.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint (without base URL)
            **kwargs: Additional arguments for requests

        Returns:
            Tuple[bool, Dict]: (success_flag, response_data)
        """
        url = f"{self.base_url}{endpoint}"

        try:
            # Add timeout if not specified
            kwargs.setdefault("timeout", self.timeout)

            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)

            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError:
                # Non-JSON response
                data = {"error": f"Invalid response format: {response.text[:100]}"}

            # Check HTTP status
            if response.status_code >= 400:
                error_msg = data.get("error", f"HTTP {response.status_code} error")
                logger.warning(f"API request failed: {method} {url} - {error_msg}")
                return False, {"error": error_msg, "status_code": response.status_code}

            logger.debug(f"API request successful: {method} {url}")
            return True, data

        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to backend server. Please ensure the Flask app is running."
            logger.error(f"Connection error: {error_msg}")
            return False, {"error": error_msg}

        except requests.exceptions.Timeout:
            error_msg = f"Request timed out after {self.timeout} seconds"
            logger.error(f"Timeout error: {error_msg}")
            return False, {"error": error_msg}

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected API error: {error_msg}")
            return False, {"error": error_msg}

    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if the backend API is healthy and responsive.

        Returns:
            Tuple[bool, Dict]: (success, response_data)
        """
        return self._make_request("GET", "/health")

    # User Management API Methods

    def get_all_users(self, active_only: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """
        Get all users from the backend.

        Args:
            active_only (bool): If True, only return active users

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "users": List[Dict], "count": int}
        """
        params = {"active_only": str(active_only).lower()}
        return self._make_request("GET", "/api/users", params=params)

    def get_user(self, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Get a specific user by ID.

        Args:
            user_id (int): User ID to retrieve

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "user": Dict}
        """
        return self._make_request("GET", f"/api/users/{user_id}")

    def create_user(
        self, name: str, birth: Optional[int] = None, active: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new user.

        Args:
            name (str): User's name (required)
            birth (Optional[int]): Birth year
            active (bool): Whether user is active

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "user": Dict, "message": str}
        """
        data = {"name": name, "active": active}
        if birth is not None:
            data["birth"] = birth

        return self._make_request("POST", "/api/users", json=data)

    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        birth: Optional[int] = None,
        active: Optional[bool] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update an existing user.

        Args:
            user_id (int): User ID to update
            name (Optional[str]): New name
            birth (Optional[int]): New birth year
            active (Optional[bool]): New active status

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "user": Dict, "message": str}
        """
        data = {}
        if name is not None:
            data["name"] = name
        if birth is not None:
            data["birth"] = birth
        if active is not None:
            data["active"] = active

        if not data:
            return False, {"error": "No fields provided for update"}

        return self._make_request("PUT", f"/api/users/{user_id}", json=data)

    def delete_user(self, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete a user by ID.

        Args:
            user_id (int): User ID to delete

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "message": str}
        """
        return self._make_request("DELETE", f"/api/users/{user_id}")

    def search_user_by_name(self, name: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Search for a user by name.

        Args:
            name (str): Name to search for

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "user": Dict}
        """
        params = {"name": name}
        return self._make_request("GET", "/api/users/search", params=params)


# Global API client instance
api_client = APIClient()


def get_api_client() -> APIClient:
    """
    Get the global API client instance.

    Returns:
        APIClient: Configured API client instance
    """
    return api_client
