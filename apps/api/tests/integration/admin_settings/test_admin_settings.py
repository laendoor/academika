from typing import Any

import pytest
from db.base import generate_uuid
from db.models.setting import Setting
from db.models.user import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.tokens import create_access_token


async def _seed_setting(db_session: AsyncSession, key: str = "auth.allowed_domains", value: Any = None) -> Setting:
    setting = Setting(
        id=generate_uuid(),
        key=key,
        value=["@unq.edu.ar"] if value is None else value,
        description="test",
    )
    db_session.add(setting)
    await db_session.commit()
    return setting


# ── GET /admin/settings ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_settings_success(client: AsyncClient, test_admin: User, admin_token: str, db_session: AsyncSession):
    await _seed_setting(db_session)
    response = await client.get("/api/v1/admin/settings", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    body = response.json()
    assert {item["key"] for item in body} == {"auth.allowed_domains"}
    assert body[0]["value"] == ["@unq.edu.ar"]
    assert body[0]["description"] == "test"


@pytest.mark.asyncio
async def test_list_settings_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/admin/settings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_settings_forbidden(client: AsyncClient, test_user: User):
    token = create_access_token(test_user.id, test_user.role, test_user.email)
    response = await client.get("/api/v1/admin/settings", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


# ── PUT /admin/settings/{key} ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_setting_success(
    client: AsyncClient, test_admin: User, admin_token: str, db_session: AsyncSession
):
    await _seed_setting(db_session)
    response = await client.put(
        "/api/v1/admin/settings/auth.allowed_domains",
        json={"value": ["*"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["value"] == ["*"]


@pytest.mark.asyncio
async def test_update_setting_not_found(client: AsyncClient, test_admin: User, admin_token: str):
    response = await client.put(
        "/api/v1/admin/settings/no.existe",
        json={"value": "x"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_setting_unauthorized(client: AsyncClient):
    response = await client.put("/api/v1/admin/settings/auth.allowed_domains", json={"value": []})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_setting_forbidden(client: AsyncClient, test_user: User):
    token = create_access_token(test_user.id, test_user.role, test_user.email)
    response = await client.put(
        "/api/v1/admin/settings/auth.allowed_domains",
        json={"value": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ── PUT /admin/settings/auth.allowed_domains (validación) ─────────────────────


@pytest.mark.asyncio
async def test_update_domains_rejects_empty(
    client: AsyncClient, test_admin: User, admin_token: str, db_session: AsyncSession
):
    await _seed_setting(db_session)
    response = await client.put(
        "/api/v1/admin/settings/auth.allowed_domains",
        json={"value": []},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_domains_rejects_without_at(
    client: AsyncClient, test_admin: User, admin_token: str, db_session: AsyncSession
):
    await _seed_setting(db_session)
    response = await client.put(
        "/api/v1/admin/settings/auth.allowed_domains",
        json={"value": ["gmail.com"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_domains_normalizes(
    client: AsyncClient, test_admin: User, admin_token: str, db_session: AsyncSession
):
    setting = await _seed_setting(db_session)
    setting_id = setting.id
    response = await client.put(
        "/api/v1/admin/settings/auth.allowed_domains",
        json={"value": [" @GMAIL.COM "]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["value"] == ["@gmail.com"]
    db_session.expire_all()
    assert (await db_session.get(Setting, setting_id)).value == ["@gmail.com"]


@pytest.mark.asyncio
async def test_update_other_key_skips_domain_validation(
    client: AsyncClient, test_admin: User, admin_token: str, db_session: AsyncSession
):
    await _seed_setting(db_session, key="otra.clave", value="x")
    response = await client.put(
        "/api/v1/admin/settings/otra.clave",
        json={"value": []},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
