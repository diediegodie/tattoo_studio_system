from backend.routes.role_decorators import admin_required

"""
User API endpoints for Tattoo Studio Management System.

Implements CRUD operations for User model.
Follows project modularity and error handling conventions.
"""

from flask import Blueprint, request, jsonify
from backend.routes.role_decorators import admin_required
from backend.database.models.user_model import (
    create_user,
    read_user,
    read_user_by_name,
    update_user,
    delete_user,
    list_all_users,
)
from utils.logger import setup_logger

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/users")
logger = setup_logger(__name__)


@user_bp.route("", methods=["GET"])
@user_bp.route("/", methods=["GET"])
def get_users():
    """Get all users."""
    try:
        active_only = request.args.get("active_only", "true").lower() == "true"
        users = list_all_users(active_only=active_only)
        data = [
            {
                "id": u.id,
                "name": u.name,
                "birth": u.birth,
                "active": u.active,
            }
            for u in users
        ]
        return jsonify({"success": True, "users": data, "count": len(data)}), 200
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@user_bp.route("", methods=["POST"])
@user_bp.route("/", methods=["POST"])
def create_user_endpoint():
    """Create a new user."""
    data = request.get_json()
    try:
        if not data.get("name"):
            return jsonify({"success": False, "error": "Name is required"}), 400

        user = create_user(
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password"),
            role=data.get("role", "staff"),
            birth=data.get("birth"),
            active=data.get("active", True),
        )
        return (
            jsonify(
                {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "role": user.role,
                        "birth": user.birth,
                        "active": user.active,
                    },
                    "message": "User created successfully",
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get a user by ID."""
    try:
        user = read_user(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        return (
            jsonify(
                {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "birth": user.birth,
                        "active": user.active,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error reading user: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@user_bp.route("/<int:user_id>", methods=["PUT"])
def update_user_endpoint(user_id):
    """Update a user by ID."""
    data = request.get_json()
    try:
        user = update_user(user_id, **data)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        return (
            jsonify(
                {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "birth": user.birth,
                        "active": user.active,
                    },
                    "message": "User updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user_endpoint(user_id):
    """Delete a user by ID."""
    try:
        result = delete_user(user_id)
        if not result:
            return jsonify({"success": False, "error": "User not found"}), 404
        return jsonify({"success": True, "message": "User deleted successfully"}), 200
    except Exception as e:
        # Reason: Propagate correct error codes from decorator
        logger.error(f"Error deleting user: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@user_bp.route("/search", methods=["GET"])
def search_user_by_name():
    """Search for a user by name."""
    try:
        name = request.args.get("name")
        if not name:
            return (
                jsonify({"success": False, "error": "Name parameter is required"}),
                400,
            )

        user = read_user_by_name(name)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        return (
            jsonify(
                {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "birth": user.birth,
                        "active": user.active,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error searching user: {e}")
        return jsonify({"success": False, "error": str(e)}), 400
