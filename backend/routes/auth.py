"""
Authentication API endpoints for Tattoo Studio Management System.
Implements /auth/login and /auth/register with JWT.
Follows project modularity and error handling conventions.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from backend.database.models.user_model import (
    create_user,
    read_user_by_email,
)
from utils.logger import setup_logger
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")
logger = setup_logger(__name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user (admin or staff)."""
    data = request.get_json()
    required_fields = ["name", "email", "password", "role"]
    if not all(data.get(f) for f in required_fields):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    if data["role"] not in ("admin", "staff"):
        return jsonify({"success": False, "error": "Invalid role"}), 400
    if read_user_by_email(data["email"]):
        return jsonify({"success": False, "error": "Email already registered"}), 409
    try:
        user = create_user(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            role=data["role"],
            birth=data.get("birth"),
            active=True,
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
                    },
                    "message": "User registered successfully",
                }
            ),
            201,
        )
    except IntegrityError:
        return jsonify({"success": False, "error": "Email already registered"}), 409
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password required"}), 400
    user = read_user_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return (
        jsonify(
            {
                "success": True,
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            }
        ),
        200,
    )
