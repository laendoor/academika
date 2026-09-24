import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.tokens import create_access_token
from app.db.base import generate_uuid
from app.models.log_event import LogEvent
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


# ── DELETE /admin/users/{id} ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_requires_auth(client: AsyncClient, test_user: User):
    response = await client.delete(f"/api/v1/admin/users/{test_user.id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_forbidden(client: AsyncClient, test_user: User, test_admin: User):
    token = create_access_token(test_user.id, test_user.role, test_user.email)
    response = await client.delete(
        f"/api/v1/admin/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_not_found(client: AsyncClient, test_admin: User, admin_token: str):
    response = await client.delete(
        f"/api/v1/admin/users/{generate_uuid()}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_success(client: AsyncClient, test_admin: User, admin_token: str, test_user: User):
    response = await client.delete(
        f"/api/v1/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    list_response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    emails = {item["email"] for item in list_response.json()["items"]}
    assert test_user.email not in emails


@pytest.mark.asyncio
async def test_delete_self_forbidden(client: AsyncClient, test_admin: User, admin_token: str):
    response = await client.delete(
        f"/api/v1/admin/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_user_with_log_events_conflict(
    client: AsyncClient, db_session: AsyncSession, test_admin: User, admin_token: str, test_user: User
):
    db_session.add(
        LogEvent(
            id=generate_uuid(),
            user_id=test_user.id,
            action="import_guarani",
            status="ok",
            details={"files": ["cursadas-2024.csv"], "processed": 1, "skipped": 0, "error": None},
        )
    )
    await db_session.commit()

    response = await client.delete(
        f"/api/v1/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 409

    list_response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    emails = {item["email"] for item in list_response.json()["items"]}
    assert test_user.email in emails
