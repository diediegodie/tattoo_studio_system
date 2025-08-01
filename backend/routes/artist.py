from backend.routes.role_decorators import admin_required

"""
Artist API endpoints for Tattoo Studio Management System.
Implements CRUD operations for Artist model.
Follows project modularity and error handling conventions.
"""

from flask import Blueprint, request, jsonify
from backend.database.models.artist_model import (
    create_artist,
    read_artist,
    update_artist,
    delete_artist,
    list_all_artists,
)
from utils.logger import setup_logger

artist_bp = Blueprint("artist_bp", __name__, url_prefix="/api/artists")
logger = setup_logger(__name__)


@artist_bp.route("/", methods=["GET"])
def get_artists():
    """Get all artists."""
    try:
        artists = list_all_artists()
        data = [
            {
                "id": a.id,
                "name": a.name,
                "phone": a.phone,
                "email": a.email,
                "bio": a.bio,
                "portfolio": a.portfolio,
            }
            for a in artists
        ]
        return jsonify({"success": True, "artists": data, "count": len(data)}), 200
    except Exception as e:
        logger.error(f"Error listing artists: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@artist_bp.route("/", methods=["POST"])
def create_artist_endpoint():
    """Create a new artist."""
    data = request.get_json()
    try:
        artist = create_artist(
            name=data.get("name"),
            phone=data.get("phone"),
            email=data.get("email"),
            bio=data.get("bio"),
            portfolio=data.get("portfolio"),
        )
        return (
            jsonify(
                {
                    "success": True,
                    "artist": {
                        "id": artist.id,
                        "name": artist.name,
                        "phone": artist.phone,
                        "email": artist.email,
                        "bio": artist.bio,
                        "portfolio": artist.portfolio,
                    },
                    "message": "Artist created successfully",
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Error creating artist: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@artist_bp.route("/<int:artist_id>", methods=["GET"])
def get_artist(artist_id):
    """Get an artist by ID."""
    try:
        artist = read_artist(artist_id)
        if not artist:
            return jsonify({"success": False, "error": "Artist not found"}), 404
        return (
            jsonify(
                {
                    "success": True,
                    "artist": {
                        "id": artist.id,
                        "name": artist.name,
                        "phone": artist.phone,
                        "email": artist.email,
                        "bio": artist.bio,
                        "portfolio": artist.portfolio,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error reading artist: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@artist_bp.route("/<int:artist_id>", methods=["PUT"])
def update_artist_endpoint(artist_id):
    """Update an artist by ID."""
    data = request.get_json()
    try:
        artist = update_artist(artist_id, **data)
        if not artist:
            return jsonify({"success": False, "error": "Artist not found"}), 404
        return (
            jsonify(
                {
                    "success": True,
                    "artist": {
                        "id": artist.id,
                        "name": artist.name,
                        "phone": artist.phone,
                        "email": artist.email,
                        "bio": artist.bio,
                        "portfolio": artist.portfolio,
                    },
                    "message": "Artist updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error updating artist: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@admin_required
@artist_bp.route("/<int:artist_id>", methods=["DELETE"])
def delete_artist_endpoint(artist_id):
    """Delete an artist by ID."""
    try:
        result = delete_artist(artist_id)
        if not result:
            return jsonify({"success": False, "error": "Artist not found"}), 404
        return jsonify({"success": True, "message": "Artist deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting artist: {e}")
        return jsonify({"success": False, "error": str(e)}), 400
