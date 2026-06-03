from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.auth.tokens import create_access_token, create_refresh_token, create_reset_token
from app.db.base import generate_uuid
from app.models.user import User

# ── POST /login ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "hari@unq.edu.ar", "password": "seldon123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "hari@unq.edu.ar", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_domain(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "hari@gmail.com", "password": "seldon123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, db_session, test_user: User):
    test_user.is_active = False
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "hari@unq.edu.ar", "password": "seldon123"},
    )
    assert response.status_code == 401


# ── POST /refresh ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient, test_user: User):
    token = create_refresh_token(test_user.id)
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": token})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": "token.invalido.xxx"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_wrong_type(client: AsyncClient, test_user: User):
    # Un access token no debe ser aceptado como refresh token
    token = create_access_token(test_user.id, test_user.role)
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": token})
    assert response.status_code == 401


# ── POST /forgot-password ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_forgot_password_sends_email(client: AsyncClient, test_user: User):
    with patch("app.services.auth.resend") as mock_resend:
        response = await client.post("/api/v1/auth/forgot-password", json={"email": "hari@unq.edu.ar"})
    assert response.status_code == 204
    mock_resend.Emails.send.assert_called_once()


@pytest.mark.asyncio
async def test_forgot_password_unknown_email(client: AsyncClient):
    with patch("app.services.auth.resend") as mock_resend:
        response = await client.post("/api/v1/auth/forgot-password", json={"email": "nadie@unq.edu.ar"})
    assert response.status_code == 204
    mock_resend.Emails.send.assert_not_called()


# ── POST /reset-password ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reset_password_success(client: AsyncClient, test_user: User):
    token = create_reset_token(test_user.id, test_user.email)
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "nueva_pass123"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "token.invalido.xxx", "new_password": "nueva_pass"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reset_password_wrong_type(client: AsyncClient, test_user: User):
    # Un refresh token no debe funcionar como reset token
    token = create_refresh_token(generate_uuid())
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "nueva_pass"},
    )
    assert response.status_code == 401
