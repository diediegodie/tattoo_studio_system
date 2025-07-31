"""
Flask backend application for Tattoo Studio Management System.

This module provides RESTful API endpoints for user management and integrates
with the SQLAlchemy database models. Follows the project structure with
feature-based organization and proper error handling.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.database import (
    initialize_database,
    create_user,
    read_user,
    read_user_by_name,
    update_user,
    delete_user,
    list_all_users,
)
from utils.logger import setup_logger
from configs.config import AppConfig

# Initialize logger and config
logger = setup_logger(__name__)
config = AppConfig()

# Create Flask app
app = Flask(__name__)
app.config["DEBUG"] = config.DEBUG

# Enable CORS for frontend communication
CORS(app)

# Initialize database when app starts
with app.app_context():
    try:
        initialize_database()
        logger.info("Flask application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return (
        jsonify(
            {
                "status": "healthy",
                "app": config.APP_NAME,
                "timestamp": datetime.now().isoformat(),
            }
        ),
        200,
    )


@app.route("/api/users", methods=["GET"])
def get_users():
    """
    Get all users.

    Query Parameters:
        active_only (bool): If true, only return active users (default: true)

    Returns:
        JSON response with list of users
    """
    try:
        active_only = request.args.get("active_only", "true").lower() == "true"
        users = list_all_users(active_only=active_only)

        # Convert users to dict format for JSON response
        users_data = []
        for user in users:
            users_data.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "birth": user.birth,
                    "active": user.active,
                }
            )

        logger.info(f"Retrieved {len(users_data)} users")
        return (
            jsonify({"success": True, "users": users_data, "count": len(users_data)}),
            200,
        )

    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve users"}), 500


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get a specific user by ID.

    Args:
        user_id (int): User ID

    Returns:
        JSON response with user data
    """
    try:
        user = read_user(user_id)

        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        user_data = {
            "id": user.id,
            "name": user.name,
            "birth": user.birth,
            "active": user.active,
        }

        logger.info(f"Retrieved user: {user.name}")
        return jsonify({"success": True, "user": user_data}), 200

    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve user"}), 500


@app.route("/api/users", methods=["POST"])
def create_new_user():
    """
    Create a new user.

    Expected JSON body:
        {
            "name": "User Name",
            "birth": 1990,  # Optional
            "active": true  # Optional, defaults to true
        }

    Returns:
        JSON response with created user data
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data or not data.get("name"):
            return jsonify({"success": False, "error": "Name is required"}), 400

        # Extract data with defaults
        name = data["name"].strip()
        birth = data.get("birth")
        active = data.get("active", True)

        # Validate name length
        if len(name) < 2:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Name must be at least 2 characters long",
                    }
                ),
                400,
            )

        # Validate birth year if provided
        if birth is not None:
            current_year = datetime.now().year
            if not isinstance(birth, int) or birth < 1900 or birth > current_year:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Birth year must be between 1900 and {current_year}",
                        }
                    ),
                    400,
                )

        # Create the user (duplicate names are allowed, only ID is unique)
        user = create_user(name=name, birth=birth, active=active)

        user_data = {
            "id": user.id,
            "name": user.name,
            "birth": user.birth,
            "active": user.active,
        }

        logger.info(f"Created new user: {user.name}")
        return (
            jsonify(
                {
                    "success": True,
                    "user": user_data,
                    "message": "User created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({"success": False, "error": "Failed to create user"}), 500


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_existing_user(user_id):
    """
    Update an existing user.

    Args:
        user_id (int): User ID

    Expected JSON body:
        {
            "name": "Updated Name",  # Optional
            "birth": 1991,          # Optional
            "active": false         # Optional
        }

    Returns:
        JSON response with updated user data
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Validate fields if provided
        update_fields = {}

        if "name" in data:
            name = data["name"].strip()
            if len(name) < 2:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Name must be at least 2 characters long",
                        }
                    ),
                    400,
                )
            update_fields["name"] = name

        if "birth" in data:
            birth = data["birth"]
            if birth is not None:
                current_year = datetime.now().year
                if not isinstance(birth, int) or birth < 1900 or birth > current_year:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": f"Birth year must be between 1900 and {current_year}",
                            }
                        ),
                        400,
                    )
            update_fields["birth"] = birth

        if "active" in data:
            update_fields["active"] = bool(data["active"])

        if not update_fields:
            return (
                jsonify({"success": False, "error": "No valid fields to update"}),
                400,
            )

        # Update the user
        updated_user = update_user(user_id, **update_fields)

        if not updated_user:
            return jsonify({"success": False, "error": "User not found"}), 404

        user_data = {
            "id": updated_user.id,
            "name": updated_user.name,
            "birth": updated_user.birth,
            "active": updated_user.active,
        }

        logger.info(f"Updated user: {updated_user.name}")
        return (
            jsonify(
                {
                    "success": True,
                    "user": user_data,
                    "message": "User updated successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return jsonify({"success": False, "error": "Failed to update user"}), 500


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_existing_user(user_id):
    """
    Delete a user by ID.

    Args:
        user_id (int): User ID

    Returns:
        JSON response confirming deletion
    """
    try:
        success = delete_user(user_id)

        if not success:
            return jsonify({"success": False, "error": "User not found"}), 404

        logger.info(f"Deleted user with ID: {user_id}")
        return jsonify({"success": True, "message": "User deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        return jsonify({"success": False, "error": "Failed to delete user"}), 500


@app.route("/api/users/search", methods=["GET"])
def search_users():
    """
    Search users by name.

    Query Parameters:
        name (str): Name to search for

    Returns:
        JSON response with matching user
    """
    try:
        name = request.args.get("name")

        if not name:
            return (
                jsonify({"success": False, "error": "Name parameter is required"}),
                400,
            )

        user = read_user_by_name(name.strip())

        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        user_data = {
            "id": user.id,
            "name": user.name,
            "birth": user.birth,
            "active": user.active,
        }

        logger.info(f"Found user by name: {user.name}")
        return jsonify({"success": True, "user": user_data}), 200

    except Exception as e:
        logger.error(f"Error searching for user: {e}")
        return jsonify({"success": False, "error": "Failed to search for user"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({"success": False, "error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    try:
        logger.info(f"Starting {config.APP_NAME} Flask backend")
        logger.info(f"Debug mode: {config.DEBUG}")
        app.run(host="127.0.0.1", port=5000, debug=config.DEBUG)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {e}")
        sys.exit(1)
