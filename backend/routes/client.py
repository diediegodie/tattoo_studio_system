from backend.routes.role_decorators import admin_required

"""
Client API endpoints for Tattoo Studio Management System.

Implements CRUD operations for Client model.
Follows project modularity and error handling conventions.
"""

from flask import Blueprint, request, jsonify
from backend.database.models.client_model import (
    create_client,
    read_client,
    update_client,
    delete_client,
    list_all_clients,
)
from utils.logger import setup_logger

client_bp = Blueprint("client_bp", __name__, url_prefix="/api/clients")
logger = setup_logger(__name__)


@client_bp.route("/", methods=["GET"])
def get_clients():
    """Get all clients."""
    try:
        clients = list_all_clients()
        data = [
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "address": c.address,
                "allergies": c.allergies,
                "medical_info": c.medical_info,
                "qr_id": c.qr_id,
            }
            for c in clients
        ]
        return jsonify({"success": True, "clients": data, "count": len(data)}), 200
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@client_bp.route("/", methods=["POST"])
def create_client_endpoint():
    """Create a new client."""
    data = request.get_json()
    try:
        client = create_client(
            name=data.get("name"),
            phone=data.get("phone"),
            address=data.get("address"),
            allergies=data.get("allergies"),
            medical_info=data.get("medical_info"),
            qr_id=data.get("qr_id"),
        )
        return (
            jsonify(
                {
                    "success": True,
                    "client": {
                        "id": client.id,
                        "name": client.name,
                        "phone": client.phone,
                        "address": client.address,
                        "allergies": client.allergies,
                        "medical_info": client.medical_info,
                        "qr_id": client.qr_id,
                    },
                    "message": "Client created successfully",
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@client_bp.route("/<int:client_id>", methods=["GET"])
def get_client(client_id):
    """Get a client by ID."""
    try:
        client = read_client(client_id)
        if not client:
            return jsonify({"success": False, "error": "Client not found"}), 404
        return (
            jsonify(
                {
                    "success": True,
                    "client": {
                        "id": client.id,
                        "name": client.name,
                        "phone": client.phone,
                        "address": client.address,
                        "allergies": client.allergies,
                        "medical_info": client.medical_info,
                        "qr_id": client.qr_id,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error reading client: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@client_bp.route("/<int:client_id>", methods=["PUT"])
def update_client_endpoint(client_id):
    """Update a client by ID."""
    data = request.get_json()
    try:
        client = update_client(client_id, **data)
        if not client:
            return jsonify({"success": False, "error": "Client not found"}), 404
        return (
            jsonify(
                {
                    "success": True,
                    "client": {
                        "id": client.id,
                        "name": client.name,
                        "phone": client.phone,
                        "address": client.address,
                        "allergies": client.allergies,
                        "medical_info": client.medical_info,
                        "qr_id": client.qr_id,
                    },
                    "message": "Client updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error updating client: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@admin_required
@client_bp.route("/<int:client_id>", methods=["DELETE"])
def delete_client_endpoint(client_id):
    """Delete a client by ID."""
    try:
        result = delete_client(client_id)
        if not result:
            return jsonify({"success": False, "error": "Client not found"}), 404
        return jsonify({"success": True, "message": "Client deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting client: {e}")
        return jsonify({"success": False, "error": str(e)}), 400
