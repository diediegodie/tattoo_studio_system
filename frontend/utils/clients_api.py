"""
Client API methods for Tattoo Studio Management System Frontend.

This module contains only the client-related API methods for use in APIClient.
Split out to keep files under 500 lines as per project instructions.
"""

from typing import Dict, Any, Tuple, Optional


class ClientAPI:
    """Client management API methods."""

    def get_all_clients(
        self, _make_request, active_only: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Get all clients from the backend.
        Args:
            active_only (bool): If True, only return active clients
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "clients": List[Dict], "count": int}
        """
        params = {"active_only": str(active_only).lower()}
        return _make_request("GET", "/api/clients", params=params)

    def get_client(self, _make_request, client_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Get a specific client by ID.
        Args:
            client_id (int): Client ID to retrieve
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "client": Dict}
        """
        return _make_request("GET", f"/api/clients/{client_id}")

    def create_client(
        self,
        _make_request,
        name: str,
        phone: str = "",
        email: str = "",
        notes: str = "",
        active: bool = True,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new client.
        Args:
            name (str): Client's name (required)
            phone (str): Phone number
            email (str): Email address
            notes (str): Additional notes
            active (bool): Whether client is active
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "client": Dict, "message": str}
        """
        data = {
            "name": name,
            "phone": phone,
            "email": email,
            "notes": notes,
            "active": active,
        }
        return _make_request("POST", "/api/clients", json=data)

    def update_client(
        self,
        _make_request,
        client_id: int,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        notes: Optional[str] = None,
        active: Optional[bool] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update an existing client.
        Args:
            client_id (int): Client ID to update
            name (str): New name
            phone (str): New phone
            email (str): New email
            notes (str): New notes
            active (bool): New active status
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "client": Dict, "message": str}
        """
        data = {}
        if name is not None:
            data["name"] = name
        if phone is not None:
            data["phone"] = phone
        if email is not None:
            data["email"] = email
        if notes is not None:
            data["notes"] = notes
        if active is not None:
            data["active"] = active
        if not data:
            return False, {"error": "No fields provided for update"}
        return _make_request("PUT", f"/api/clients/{client_id}", json=data)

    def delete_client(
        self, _make_request, client_id: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete a client by ID.
        Args:
            client_id (int): Client ID to delete
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "message": str}
        """
        return _make_request("DELETE", f"/api/clients/{client_id}")

    def search_client_by_name(
        self, _make_request, name: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Search for a client by name.
        Args:
            name (str): Name to search for
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "client": Dict}
        """
        params = {"name": name}
        return _make_request("GET", "/api/clients/search", params=params)
