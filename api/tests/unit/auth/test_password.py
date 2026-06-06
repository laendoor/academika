import pytest

from app.auth.password import hash_password, verify_password


def test_hash_returns_string():
    result = hash_password("secreto123")
    assert isinstance(result, str)
    assert result != "secreto123"


def test_hash_different_each_call():
    h1 = hash_password("secreto123")
    h2 = hash_password("secreto123")
    assert h1 != h2


def test_verify_correct_password():
    hashed = hash_password("secreto123")
    assert verify_password("secreto123", hashed) is True


def test_verify_wrong_password():
    hashed = hash_password("secreto123")
    assert verify_password("otropass", hashed) is False


@pytest.mark.parametrize("password", ["", "a", "a" * 71, "ñoño123!", "p@$$w0rd"])
def test_roundtrip(password: str):
    assert verify_password(password, hash_password(password)) is True
