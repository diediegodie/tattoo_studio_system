"""
Role-based access control decorators for Flask routes.
"""

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import jsonify


def admin_required(fn):
    """Decorator to require admin role."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if not identity or identity.get("role") != "admin":
            return jsonify({"success": False, "error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def staff_required(fn):
    """Decorator to require staff or admin role."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if not identity or identity.get("role") not in ("admin", "staff"):
            return jsonify({"success": False, "error": "Staff access required"}), 403
        return fn(*args, **kwargs)

    return wrapper
