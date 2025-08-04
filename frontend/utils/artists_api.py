"""
Artist API methods for Tattoo Studio Management System Frontend.

This module contains only the artist-related API methods for use in APIClient.
Split out to keep files under 500 lines as per project instructions.
"""

from typing import Dict, Any, Tuple, Optional


class ArtistAPI:
    """Artist management API methods."""

    def get_all_artists(self, _make_request) -> Tuple[bool, Dict[str, Any]]:
        """
        Get all artists from the backend.
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "artists": List[Dict], "count": int}
        """
        return _make_request("GET", "/api/artists")

    def get_artist(self, _make_request, artist_id: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Get a specific artist by ID.
        Args:
            artist_id (int): Artist ID to retrieve
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "artist": Dict}
        """
        return _make_request("GET", f"/api/artists/{artist_id}")

    def create_artist(
        self,
        _make_request,
        name: str,
        phone: str = "",
        email: str = "",
        bio: str = "",
        portfolio: str = "",
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new artist.
        Args:
            name (str): Artist's name (required)
            phone (str): Phone number
            email (str): Email address
            bio (str): Biography
            portfolio (str): Portfolio URL/description
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "artist": Dict, "message": str}
        """
        data = {
            "name": name,
            "phone": phone,
            "email": email,
            "bio": bio,
            "portfolio": portfolio,
        }
        return _make_request("POST", "/api/artists", json=data)

    def update_artist(
        self,
        _make_request,
        artist_id: int,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        bio: Optional[str] = None,
        portfolio: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update an existing artist.
        Args:
            artist_id (int): Artist ID to update
            name (str): New name
            phone (str): New phone
            email (str): New email
            bio (str): New biography
            portfolio (str): New portfolio
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "artist": Dict, "message": str}
        """
        data = {}
        if name is not None:
            data["name"] = name
        if phone is not None:
            data["phone"] = phone
        if email is not None:
            data["email"] = email
        if bio is not None:
            data["bio"] = bio
        if portfolio is not None:
            data["portfolio"] = portfolio
        if not data:
            return False, {"error": "No fields provided for update"}
        return _make_request("PUT", f"/api/artists/{artist_id}", json=data)

    def delete_artist(
        self, _make_request, artist_id: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Delete an artist by ID.
        Args:
            artist_id (int): Artist ID to delete
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "message": str}
        """
        return _make_request("DELETE", f"/api/artists/{artist_id}")

    def search_artist_by_name(
        self, _make_request, name: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Search for an artist by name.
        Args:
            name (str): Name to search for
        Returns:
            Tuple[bool, Dict]: (success, response_data)
            Response format: {"success": bool, "artists": List[Dict]}
        """
        params = {"name": name}
        return _make_request("GET", "/api/artists/search", params=params)
