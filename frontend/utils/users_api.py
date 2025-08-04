"""
User API methods for Tattoo Studio Management System Frontend.

This module contains only the user-related API methods for use in APIClient.
Split out to keep files under 500 lines as per project instructions.
"""

from typing import Dict, Any, Tuple, Optional


class UserAPI:
    """User management API methods."""

    def get_all_users(
        self, _make_request, active_only: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Get all users from the backend.

        Args:
            active_only (bool): If True, only return active users

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "users": List[Dict], "count": int}
        """
        params = {"active_only": str(active_only).lower()}
        return _make_request("GET", "/api/users", params=params)

    def get_user(self, _make_request, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Get a specific user by ID.

        Args:
            user_id (int): User ID to retrieve

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "user": Dict}
        """
        return _make_request("GET", f"/api/users/{user_id}")

    def create_user(
        self,
        _make_request,
        name: str,
        birth: Optional[int] = None,
        active: bool = True,
        password: Optional[str] = None,
        email: Optional[str] = None,
        role: str = "staff",
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new user.

        Args:
            name (str): User's name (required)
            birth (Optional[int]): Birth year
            active (bool): Whether user is active
            password (Optional[str]): User password
            email (Optional[str]): User email

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "user": Dict, "message": str}
        """
        data = {"name": name, "active": active, "role": role}
        if birth is not None:
            data["birth"] = birth
        if password is not None:
            data["password"] = password
        if email is not None:
            data["email"] = email

        return _make_request("POST", "/api/users", json=data)

    def update_user(
        self,
        _make_request,
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

        return _make_request("PUT", f"/api/users/{user_id}", json=data)

    def delete_user(self, _make_request, user_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete a user by ID.

        Args:
            user_id (int): User ID to delete

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "message": str, "error": Optional[str]}
        """
        success, resp = _make_request("DELETE", f"/api/users/{user_id}")
        # Reason: Ensure error field is present if deletion fails
        if not success and "error" not in resp:
            resp["error"] = resp.get("message", "Unknown error")
        return success, resp

    def search_user_by_name(
        self, _make_request, name: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Search for a user by name.

        Args:
            name (str): Name to search for

        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "user": Dict, "status_code": int}
        """
        params = {"name": name}
        success, resp = _make_request("GET", "/api/users/search", params=params)
        # Reason: Ensure status_code is always present for consistency
        if "status_code" not in resp:
            resp["status_code"] = 200 if success else 404
        return success, resp
