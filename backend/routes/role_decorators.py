"""
Role-based access control decorators for Flask routes.
"""

from backend.utils.jwt_utils import verify_access_token, JWTValidationError
from functools import wraps
from flask import jsonify


def admin_required(fn):
    """Decorator to require admin role."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        from flask import request

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "error": "Missing or invalid token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            identity = verify_access_token(token)
        except JWTValidationError as e:
            msg = str(e)
            if "expired" in msg.lower():
                return jsonify({"success": False, "error": msg}), 401
            return jsonify({"success": False, "error": msg}), 422
        if not identity or identity.get("role") != "admin":
            return jsonify({"success": False, "error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def staff_required(fn):
    """Decorator to require staff or admin role."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        from flask import request

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "error": "Missing or invalid token"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            identity = verify_access_token(token)
        except JWTValidationError as e:
            return jsonify({"success": False, "error": str(e)}), 401
        if not identity or identity.get("role") not in ("admin", "staff"):
            return jsonify({"success": False, "error": "Staff access required"}), 403
        return fn(*args, **kwargs)

    return wrapper
