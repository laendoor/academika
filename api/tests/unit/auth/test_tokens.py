import uuid

import jwt
import pytest

from app.auth.tokens import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
)


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


def test_access_token_payload(user_id):
    token = create_access_token(user_id, "director")
    payload = decode_token(token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["role"] == "director"
    assert payload["type"] == "access"


def test_refresh_token_payload(user_id):
    token = create_refresh_token(user_id)
    payload = decode_token(token, expected_type="refresh")
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_reset_token_payload(user_id):
    token = create_reset_token(user_id, "lean@unq.edu.ar")
    payload = decode_token(token, expected_type="reset")
    assert payload["sub"] == str(user_id)
    assert payload["email"] == "lean@unq.edu.ar"
    assert payload["type"] == "reset"


def test_wrong_type_raises(user_id):
    refresh = create_refresh_token(user_id)
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(refresh, expected_type="access")


def test_tampered_token_raises(user_id):
    token = create_access_token(user_id, "admin")
    with pytest.raises(jwt.InvalidSignatureError):
        decode_token(token[:-4] + "xxxx")


def test_no_type_check_accepts_any(user_id):
    token = create_refresh_token(user_id)
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
