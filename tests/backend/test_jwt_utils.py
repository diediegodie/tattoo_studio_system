"""
Testes para utilitário JWT (create_access_token).
"""

import pytest
from datetime import timedelta
from backend.utils.jwt_utils import create_access_token, JWTValidationError


# Normal case: token válido
def test_create_access_token_normal():
    payload = {"id": 123, "role": "admin"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    assert token.count(".") == 2  # JWT tem 3 partes


# Edge case: expiração customizada
def test_create_access_token_custom_exp():
    payload = {"id": 1, "role": "staff"}
    token = create_access_token(payload, expires_delta=timedelta(seconds=10))
    assert isinstance(token, str)


# Failure case: payload não é dict
def test_create_access_token_invalid_type():
    with pytest.raises(JWTValidationError):
        create_access_token(["id", 1])


# Failure case: payload sem id
def test_create_access_token_missing_id():
    with pytest.raises(JWTValidationError):
        create_access_token({"role": "admin"})


# Failure case: payload com campo sensível
@pytest.mark.parametrize("bad_field", ["password", "secret", "token"])
def test_create_access_token_sensitive_field(bad_field):
    payload = {"id": 1, bad_field: "should_not_be_here"}
    with pytest.raises(JWTValidationError):
        create_access_token(payload)
