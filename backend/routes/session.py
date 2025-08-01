from backend.routes.role_decorators import admin_required

"""
Session API endpoints for Tattoo Studio Management System.
Implements CRUD operations for Session model.
Follows project modularity and error handling conventions.
"""

from flask import Blueprint, request, jsonify
from backend.database.models.session_model import (
    create_session,
    read_session,
    update_session,
    delete_session,
    list_all_sessions,
)

# Removed unused import: get_session
from utils.logger import setup_logger
from datetime import datetime

session_bp = Blueprint("session_bp", __name__, url_prefix="/api/sessions")
logger = setup_logger(__name__)


@session_bp.route("/", methods=["GET"])
def get_sessions():
    """Get all sessions."""
    try:
        sessions = list_all_sessions()
        data = [
            {
                "id": s.id,
                "client_id": s.client_id,
                "artist_id": s.artist_id,
                "date": s.date.isoformat() if s.date is not None else None,
                "status": s.status,
                "notes": s.notes,
            }
            for s in sessions
        ]
        return jsonify({"success": True, "sessions": data, "count": len(data)}), 200
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@session_bp.route("/", methods=["POST"])
def create_session_endpoint():
    """Create a new session."""
    data = request.get_json()
    try:
        # Parse date string to datetime
        date_str = data.get("date")
        if not date_str:
            return jsonify({"success": False, "error": "Date is required"}), 400
        try:
            date = datetime.fromisoformat(date_str)
        except Exception:
            return jsonify({"success": False, "error": "Invalid date format"}), 400
        session_obj = create_session(
            client_id=data.get("client_id"),
            artist_id=data.get("artist_id"),
            date=date,
            status=data.get("status", "planned"),
            notes=data.get("notes"),
        )
        return (
            jsonify(
                {
                    "success": True,
                    "session": {
                        "id": session_obj.id,
                        "client_id": session_obj.client_id,
                        "artist_id": session_obj.artist_id,
                        "date": (
                            session_obj.date.isoformat()
                            if session_obj.date is not None
                            else None
                        ),
                        "status": session_obj.status,
                        "notes": session_obj.notes,
                    },
                    "message": "Session created successfully",
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@session_bp.route("/<int:session_id>", methods=["GET"])
def get_session(session_id):
    """Get a session by ID."""
    try:
        session_obj = read_session(session_id)
        if not session_obj:
            return jsonify({"success": False, "error": "Session not found"}), 404
        return (
            jsonify(
                {
                    "success": True,
                    "session": {
                        "id": session_obj.id,
                        "client_id": session_obj.client_id,
                        "artist_id": session_obj.artist_id,
                        "date": (
                            session_obj.date.isoformat()
                            if session_obj.date is not None
                            else None
                        ),
                        "status": session_obj.status,
                        "notes": session_obj.notes,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error reading session: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@session_bp.route("/<int:session_id>", methods=["PUT"])
def update_session_endpoint(session_id):
    """Update a session by ID."""
    data = request.get_json()
    try:
        if "date" in data:
            try:
                data["date"] = datetime.fromisoformat(data["date"])
            except Exception:
                return jsonify({"success": False, "error": "Invalid date format"}), 400
        session_obj = update_session(session_id, **data)
        if not session_obj:
            return jsonify({"success": False, "error": "Session not found"}), 404
        return (
            jsonify(
                {
                    "success": True,
                    "session": {
                        "id": session_obj.id,
                        "client_id": session_obj.client_id,
                        "artist_id": session_obj.artist_id,
                        "date": (
                            session_obj.date.isoformat()
                            if session_obj.date is not None
                            else None
                        ),
                        "status": session_obj.status,
                        "notes": session_obj.notes,
                    },
                    "message": "Session updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@admin_required
@session_bp.route("/<int:session_id>", methods=["DELETE"])
def delete_session_endpoint(session_id):
    """Delete a session by ID."""
    try:
        result = delete_session(session_id)
        if not result:
            return jsonify({"success": False, "error": "Session not found"}), 404
        return (
            jsonify({"success": True, "message": "Session deleted successfully"}),
            200,
        )
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        return jsonify({"success": False, "error": str(e)}), 400
