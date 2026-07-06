import pytest
from httpx import AsyncClient

from app.auth.tokens import create_access_token
from app.db.base import generate_uuid
from app.models.user import User

# ── GET /admin/users ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_users_success(client: AsyncClient, test_admin: User, admin_token: str, test_user: User):
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    emails = {item["email"] for item in body["items"]}
    assert {test_admin.email, test_user.email} <= emails
    admin_item = next(item for item in body["items"] if item["email"] == test_admin.email)
    assert admin_item["role"] == "admin"
    assert admin_item["is_active"] is True


@pytest.mark.asyncio
async def test_list_users_forbidden(client: AsyncClient, test_user: User):
    token = create_access_token(test_user.id, test_user.role, test_user.email)
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ── PUT /admin/users/{id} ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_role_success(client: AsyncClient, test_admin: User, admin_token: str, test_user: User):
    response = await client.put(
        f"/api/v1/admin/users/{test_user.id}",
        json={"role": "docente"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "docente"


@pytest.mark.asyncio
async def test_update_deactivate_success(client: AsyncClient, test_admin: User, admin_token: str, test_user: User):
    response = await client.put(
        f"/api/v1/admin/users/{test_user.id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_not_found(client: AsyncClient, test_admin: User, admin_token: str):
    response = await client.put(
        f"/api/v1/admin/users/{generate_uuid()}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_forbidden(client: AsyncClient, test_user: User, test_admin: User):
    token = create_access_token(test_user.id, test_user.role, test_user.email)
    response = await client.put(
        f"/api/v1/admin/users/{test_admin.id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_self_lockout_role(client: AsyncClient, test_admin: User, admin_token: str):
    response = await client.put(
        f"/api/v1/admin/users/{test_admin.id}",
        json={"role": "docente"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_self_lockout_deactivate(client: AsyncClient, test_admin: User, admin_token: str):
    response = await client.put(
        f"/api/v1/admin/users/{test_admin.id}",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422
