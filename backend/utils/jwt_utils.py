from typing import Dict, Any


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT access token.
    Args:
        token (str): JWT token string.
    Returns:
        dict: Decoded payload if valid.
    Raises:
        JWTValidationError: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTValidationError("Token has expired.")
    except jwt.InvalidTokenError as e:
        raise JWTValidationError(f"Invalid token: {e}")


"""
JWT utility functions for secure token generation.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from configs.config import config


class JWTValidationError(Exception):
    """Custom exception for JWT validation errors."""

    pass


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a JWT access token with validation.

    Args:
        data (dict): Payload data. Must include 'id' (user id).
        expires_delta (timedelta, optional): Expiration delta. Defaults to 30 minutes.

    Returns:
        str: Encoded JWT token string.

    Raises:
        JWTValidationError: If input data is invalid.
    """
    if not isinstance(data, dict):
        raise JWTValidationError("Payload data must be a dictionary.")
    if "id" not in data:
        raise JWTValidationError("Payload must include user id.")
    if any(k in data for k in ("password", "secret", "token")):
        raise JWTValidationError(
            "Sensitive fields must not be included in token payload."
        )

    now = datetime.utcnow()
    expire = now + (expires_delta if expires_delta else timedelta(minutes=30))
    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": now})
    try:
        encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm="HS256")
    except Exception as e:
        raise JWTValidationError(f"JWT encoding failed: {e}")
    return encoded_jwt
