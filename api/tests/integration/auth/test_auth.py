from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.auth.tokens import create_access_token, create_invite_token, create_refresh_token, create_reset_token
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
    with patch("app.services.auth.send_mail") as mock_send:
        response = await client.post("/api/v1/auth/forgot-password", json={"email": "hari@unq.edu.ar"})
    assert response.status_code == 204
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_forgot_password_unknown_email(client: AsyncClient):
    with patch("app.services.auth.send_mail") as mock_send:
        response = await client.post("/api/v1/auth/forgot-password", json={"email": "nadie@unq.edu.ar"})
    assert response.status_code == 204
    mock_send.assert_not_called()


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


# ── POST /invite ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invite_success(client: AsyncClient, test_admin: User, admin_token: str):
    with patch("app.services.auth.send_mail") as mock_send:
        response = await client.post(
            "/api/v1/auth/invite",
            json={"email": "nuevo@unq.edu.ar", "role": "docente"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    assert response.status_code == 204
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_invite_wrong_domain(client: AsyncClient, test_admin: User, admin_token: str):
    response = await client.post(
        "/api/v1/auth/invite",
        json={"email": "nuevo@gmail.com", "role": "docente"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invite_user_already_exists(client: AsyncClient, test_admin: User, admin_token: str, test_user: User):
    response = await client.post(
        "/api/v1/auth/invite",
        json={"email": "hari@unq.edu.ar", "role": "docente"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_invite_forbidden(client: AsyncClient, test_user: User):
    # Un director no puede invitar — solo admin
    token = create_access_token(test_user.id, test_user.role)
    response = await client.post(
        "/api/v1/auth/invite",
        json={"email": "nuevo@unq.edu.ar", "role": "docente"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ── POST /register ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    token = create_invite_token("nuevo@unq.edu.ar", "docente")
    response = await client.post(
        "/api/v1/auth/register",
        json={"token": token, "password": "password123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_invalid_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"token": "token.invalido.xxx", "password": "password123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_wrong_type(client: AsyncClient, test_user: User):
    # Un access token no debe funcionar como invite token
    token = create_access_token(test_user.id, test_user.role)
    response = await client.post(
        "/api/v1/auth/register",
        json={"token": token, "password": "password123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_user_already_exists(client: AsyncClient, test_user: User):
    # El usuario hari@unq.edu.ar ya existe — el token de invite es válido pero el registro debe fallar
    token = create_invite_token("hari@unq.edu.ar", "director")
    response = await client.post(
        "/api/v1/auth/register",
        json={"token": token, "password": "password123"},
    )
    assert response.status_code == 409


# ── flujo completo: invite → register → login ─────────────────────────────────


@pytest.mark.asyncio
async def test_invite_then_register_flow(client: AsyncClient, test_admin: User, admin_token: str):
    email = "salvor@unq.edu.ar"
    password = "hardin456"

    with patch("app.services.auth.send_mail"):
        invite_response = await client.post(
            "/api/v1/auth/invite",
            json={"email": email, "role": "docente"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
    assert invite_response.status_code == 204

    invite_token = create_invite_token(email, "docente")
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"token": invite_token, "password": password},
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    body = login_response.json()
    assert "access_token" in body
