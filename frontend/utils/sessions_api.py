"""
Session API methods for Tattoo Studio Management System Frontend.

This module contains only the session-related API methods for use in APIClient.
Split out to keep files under 500 lines as per project instructions.
"""

from typing import Dict, Any, Tuple, Optional


class SessionAPI:
    def get_all_sessions(self, _make_request) -> Tuple[bool, Dict[str, Any]]:
        return _make_request("GET", "/api/sessions")

    def get_session(
        self, _make_request, session_id: int
    ) -> Tuple[bool, Dict[str, Any]]:
        return _make_request("GET", f"/api/sessions/{session_id}")

    def create_session(
        self,
        _make_request,
        client_id: int,
        artist_id: int,
        session_date: str,
        duration: float,
        description: str = "",
        price: float = 0.0,
        status: str = "scheduled",
    ) -> Tuple[bool, Dict[str, Any]]:
        data = {
            "client_id": client_id,
            "artist_id": artist_id,
            "session_date": session_date,
            "duration": duration,
            "description": description,
            "price": price,
            "status": status,
        }
        return _make_request("POST", "/api/sessions", json=data)

    def update_session(
        self,
        _make_request,
        session_id: int,
        client_id: Optional[int] = None,
        artist_id: Optional[int] = None,
        session_date: Optional[str] = None,
        duration: Optional[float] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        status: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        data = {}
        if client_id is not None:
            data["client_id"] = client_id
        if artist_id is not None:
            data["artist_id"] = artist_id
        if session_date is not None:
            data["session_date"] = session_date
        if duration is not None:
            data["duration"] = duration
        if description is not None:
            data["description"] = description
        if price is not None:
            data["price"] = price
        if status is not None:
            data["status"] = status
        if not data:
            return False, {"error": "No fields provided for update"}
        return _make_request("PUT", f"/api/sessions/{session_id}", json=data)

    def delete_session(
        self, _make_request, session_id: int
    ) -> Tuple[bool, Dict[str, Any]]:
        return _make_request("DELETE", f"/api/sessions/{session_id}")

    def search_session(self, _make_request, query: str) -> Tuple[bool, Dict[str, Any]]:
        params = {"query": query}
        return _make_request("GET", "/api/sessions/search", params=params)
