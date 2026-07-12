from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from app.auth.tokens import create_access_token
from app.db.base import generate_uuid
from app.models.log_event import LogEvent
from app.models.user import User

ADMIN_ACTION = "import_guarani"
_BASE_AT = datetime(2026, 7, 9, 12, 0, 0, tzinfo=UTC)


async def _seed_event(
    db_session,
    user_id,
    *,
    status="ok",
    sheet_type: str | None = "carreras",
    processed=5,
    skipped=0,
    error=None,
    created_at=None,
):
    event = LogEvent(
        id=generate_uuid(),
        created_at=created_at if created_at is not None else _BASE_AT,
        user_id=user_id,
        action=ADMIN_ACTION,
        status=status,
        details={
            "sheet_type": sheet_type,
            "files": [f"{sheet_type or 'unknown'}.csv"],
            "processed": processed,
            "skipped": skipped,
            "error": error,
        },
    )
    db_session.add(event)
    await db_session.flush()
    return event


@pytest.mark.asyncio
async def test_sources_rejects_no_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/sources")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_sources_director_can_list(client: AsyncClient, test_user: User, db_session) -> None:
    await _seed_event(db_session, test_user.id)
    await db_session.commit()
    token = create_access_token(test_user.id, test_user.role, test_user.email)

    response = await client.get("/api/v1/sources", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert "id" in item
    assert "created_at" in item
    assert item["status"] == "ok"
    assert item["details"]["sheet_type"] == "carreras"
    assert item["details"]["processed"] == 5
    assert item["details"]["error"] is None


@pytest.mark.asyncio
async def test_sources_admin_can_list(client: AsyncClient, test_admin: User, db_session) -> None:
    await _seed_event(db_session, test_admin.id)
    await db_session.commit()
    token = create_access_token(test_admin.id, test_admin.role, test_admin.email)
    response = await client.get("/api/v1/sources", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_sources_paginates(client: AsyncClient, test_user: User, db_session) -> None:
    for i in range(5):
        await _seed_event(db_session, test_user.id, sheet_type=f"tipo_{i}")
    await db_session.commit()
    token = create_access_token(test_user.id, test_user.role, test_user.email)

    response = await client.get(
        "/api/v1/sources?skip=2&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    body = response.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_sources_returns_import_details_shape(client: AsyncClient, test_user: User, db_session) -> None:
    await _seed_event(
        db_session,
        test_user.id,
        sheet_type=None,
        processed=0,
        skipped=0,
        error="encoding inválido",
    )
    await db_session.commit()
    token = create_access_token(test_user.id, test_user.role, test_user.email)

    response = await client.get("/api/v1/sources", headers={"Authorization": f"Bearer {token}"})
    item = response.json()["items"][0]
    assert set(item["details"].keys()) == {"sheet_type", "files", "processed", "skipped", "error"}
    assert item["details"]["sheet_type"] is None


@pytest.mark.asyncio
async def test_sources_orders_by_created_at_desc(client: AsyncClient, test_user: User, db_session) -> None:
    e1 = await _seed_event(db_session, test_user.id, created_at=_BASE_AT)
    e2 = await _seed_event(db_session, test_user.id, created_at=_BASE_AT + timedelta(minutes=1))
    e3 = await _seed_event(db_session, test_user.id, created_at=_BASE_AT + timedelta(minutes=2))
    await db_session.commit()
    token = create_access_token(test_user.id, test_user.role, test_user.email)

    response = await client.get("/api/v1/sources", headers={"Authorization": f"Bearer {token}"})
    ids = [item["id"] for item in response.json()["items"]]
    assert ids == [str(e3.id), str(e2.id), str(e1.id)]


@pytest.mark.asyncio
async def test_sources_filters_only_import_guarani(client: AsyncClient, test_user: User, db_session) -> None:
    await _seed_event(db_session, test_user.id)
    other = LogEvent(
        id=generate_uuid(),
        user_id=test_user.id,
        action="import_guarani",  # único action disponible en lkp por ahora
        status="ok",
        details={"sheet_type": "alumnos", "files": ["x.csv"], "processed": 1, "skipped": 0, "error": None},
    )
    db_session.add(other)
    await db_session.commit()
    token = create_access_token(test_user.id, test_user.role, test_user.email)

    response = await client.get("/api/v1/sources", headers={"Authorization": f"Bearer {token}"})
    body = response.json()
    assert body["total"] == 2
    for item in body["items"]:
        assert item["details"]["sheet_type"] in {"carreras", "alumnos"}


@pytest.mark.asyncio
async def test_sources_returns_error_status_in_response(client: AsyncClient, test_user: User, db_session) -> None:
    await _seed_event(db_session, test_user.id, status="error", error="importación fallida: boom")
    await db_session.commit()
    token = create_access_token(test_user.id, test_user.role, test_user.email)

    response = await client.get("/api/v1/sources", headers={"Authorization": f"Bearer {token}"})
    item = response.json()["items"][0]
    assert item["status"] == "error"
    assert "boom" in item["details"]["error"]


@pytest.mark.asyncio
async def test_sources_rejects_docente(client: AsyncClient, db_session) -> None:
    from app.auth.password import hash_password
    from app.db.base import generate_uuid

    docente = User(
        id=generate_uuid(),
        email="docente@unq.edu.ar",
        hashed_password=hash_password("x"),
        role="docente",
        is_active=True,
    )
    db_session.add(docente)
    await db_session.commit()
    token = create_access_token(docente.id, docente.role, docente.email)

    response = await client.get("/api/v1/sources", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
