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
- Modular design with feature-specific API modules
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
from frontend.utils.users_api import UserAPI
from frontend.utils.clients_api import ClientAPI
from frontend.utils.artists_api import ArtistAPI
from frontend.utils.sessions_api import SessionAPI

# Initialize logger and config
logger = setup_logger(__name__)
config = AppConfig()


class APIClient:
    def search_user_by_name(self, name: str) -> Tuple[bool, Dict[str, Any]]:
        """Search for a user by name using the users API."""
        return self.user_api.search_user_by_name(self._make_request, name)

    """
    Main API client for communication with the Flask backend.

    This class serves as the central point for all API interactions,
    delegating specific operations to specialized API modules while
    providing common functionality like request handling, authentication,
    and error management.
    """

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the API client with configuration and API modules."""
        self.base_url = base_url or getattr(
            config, "API_BASE_URL", "http://localhost:5000"
        )
        self.timeout = getattr(config, "API_TIMEOUT", 30)
        self.jwt_token = None

        # Initialize feature-specific API modules
        self.user_api = UserAPI()
        self.client_api = ClientAPI()
        self.artist_api = ArtistAPI()
        self.session_api = SessionAPI()

        logger.info(f"APIClient initialized with base URL: {self.base_url}")

    def set_token(self, token: str):
        """Set JWT token for authenticated requests."""
        self.jwt_token = token
        logger.info("JWT token set for authenticated requests")

    def clear_token(self):
        """Clear JWT token."""
        self.jwt_token = None
        logger.info("JWT token cleared")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests including authorization if available."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Make HTTP request to the API.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint path
            json (Dict, optional): JSON data for request body
            params (Dict, optional): Query parameters

        Returns:
            Tuple[bool, Dict]: (success, response_data)
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            logger.debug(f"Making {method} request to {url}")

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                params=params,
                timeout=self.timeout,
            )

            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"message": response.text or "No response content"}

            # Check if request was successful
            if response.status_code >= 200 and response.status_code < 300:
                logger.debug(f"Request successful: {response.status_code}")
                return True, response_data
            else:
                logger.warning(
                    f"Request failed: {response.status_code} - {response_data}"
                )
                return False, response_data

        except requests.exceptions.Timeout:
            error_msg = "Request timeout - server took too long to respond"
            logger.error(error_msg)
            return False, {"error": error_msg}

        except requests.exceptions.ConnectionError:
            error_msg = "Connection failed - unable to reach server"
            logger.error(error_msg)
            return False, {"error": error_msg}

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, {"error": error_msg}

    def health_check(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if the API server is responding."""
        return self._make_request("GET", "/health")

    # Authentication Methods
    def login(self, email: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Authenticate user and get JWT token.

        Args:
            email (str): User email
            password (str): User password

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"token": str, "user": Dict} on success
        """
        data = {"email": email, "password": password}
        success, resp = self._make_request("POST", "/auth/login", json=data)
        # Reason: Set JWT token for subsequent requests if login is successful
        if success and "access_token" in resp:
            self.set_token(resp["access_token"])
        return success, resp

    def register(
        self, name: str, email: str, password: str, role: str = "staff"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Register a new user.

        Args:
            name (str): User's full name
            email (str): User's email address
            password (str): User's password
            role (str): User's role (admin or staff)

        Returns:
            Tuple[bool, Dict]: (success, response_data)
        """
        data = {"name": name, "email": email, "password": password, "role": role}
        return self._make_request("POST", "/auth/register", json=data)

    # User Management API Methods - Delegate to UserAPI
    def get_all_users(self, active_only: bool = True) -> Tuple[bool, Dict[str, Any]]:
        return self.user_api.get_all_users(self._make_request, active_only)

    def get_user(self, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        return self.user_api.get_user(self._make_request, user_id)

    def create_user(
        self,
        name: str,
        birth: Optional[int] = None,
        active: bool = True,
        password: Optional[str] = None,
        email: Optional[str] = None,
        role: str = "staff",
    ) -> Tuple[bool, Dict[str, Any]]:
        return self.user_api.create_user(
            self._make_request, name, birth, active, password, email, role
        )

    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        birth: Optional[int] = None,
        active: Optional[bool] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        return self.user_api.update_user(
            self._make_request, user_id, name, birth, active
        )

    def delete_user(self, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        return self.user_api.delete_user(self._make_request, user_id)

    # Client Management API Methods - Delegate to ClientAPI
    def get_all_clients(self, active_only: bool = True) -> Tuple[bool, Dict[str, Any]]:
        return self.client_api.get_all_clients(self._make_request, active_only)

    def get_client(self, client_id: int) -> Tuple[bool, Dict[str, Any]]:
        return self.client_api.get_client(self._make_request, client_id)

    def create_client(
        self,
        name: str,
        phone: str = "",
        email: str = "",
        notes: str = "",
        active: bool = True,
    ) -> Tuple[bool, Dict[str, Any]]:
        return self.client_api.create_client(
            self._make_request, name, phone, email, notes, active
        )

    def update_client(
        self,
        client_id: int,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        notes: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        return self.client_api.update_client(
            self._make_request, client_id, name, phone, email, notes, active
        )

    def delete_client(self, client_id: int) -> Tuple[bool, Dict[str, Any]]:
        return self.client_api.delete_client(self._make_request, client_id)

    def search_client_by_name(self, name: str) -> Tuple[bool, Dict[str, Any]]:
        return self.client_api.search_client_by_name(self._make_request, name)

    # Artist Management API Methods - Delegate to ArtistAPI
    def get_all_artists(self) -> Tuple[bool, Dict[str, Any]]:
        return self.artist_api.get_all_artists(self._make_request)

    def get_artist(self, artist_id: int) -> Tuple[bool, Dict[str, Any]]:
        return self.artist_api.get_artist(self._make_request, artist_id)

    def create_artist(
        self,
        name: str,
        phone: str = "",
        email: str = "",
        bio: str = "",
        portfolio: str = "",
    ) -> Tuple[bool, Dict[str, Any]]:
        return self.artist_api.create_artist(
            self._make_request, name, phone, email, bio, portfolio
        )

    def update_artist(
        self,
        artist_id: int,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        bio: Optional[str] = None,
        portfolio: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        return self.artist_api.update_artist(
            self._make_request, artist_id, name, phone, email, bio, portfolio
        )

    def delete_artist(self, artist_id: int) -> Tuple[bool, Dict[str, Any]]:
        return self.artist_api.delete_artist(self._make_request, artist_id)

    # Session Management API Methods - Delegate to SessionAPI
    def get_all_sessions(self) -> Tuple[bool, Dict[str, Any]]:
        return self.session_api.get_all_sessions(self._make_request)

    def get_session(self, session_id: int) -> Tuple[bool, Dict[str, Any]]:
        return self.session_api.get_session(self._make_request, session_id)

    def create_session(
        self,
        client_id: int,
        artist_id: int,
        session_date: str,
        duration: float,
        description: str = "",
        price: float = 0.0,
        status: str = "scheduled",
    ) -> Tuple[bool, Dict[str, Any]]:
        return self.session_api.create_session(
            self._make_request,
            client_id,
            artist_id,
            session_date,
            duration,
            description,
            price,
            status,
        )

    def update_session(
        self,
        session_id: int,
        client_id: Optional[int] = None,
        artist_id: Optional[int] = None,
        session_date: Optional[str] = None,
        duration: Optional[float] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        status: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        return self.session_api.update_session(
            self._make_request,
            session_id,
            client_id,
            artist_id,
            session_date,
            duration,
            description,
            price,
            status,
        )

    def delete_session(self, session_id: int) -> Tuple[bool, Dict[str, Any]]:
        return self.session_api.delete_session(self._make_request, session_id)

    def search_session(self, query: str) -> Tuple[bool, Dict[str, Any]]:
        return self.session_api.search_session(self._make_request, query)


# Global instance for easy access
_api_client = None


def get_api_client() -> APIClient:
    """Get the global APIClient instance."""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client
