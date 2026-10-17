from hashlib import sha256
from pathlib import Path

import pytest
from db.models.log_event import LogEvent
from db.models.user import User
from httpx import AsyncClient
from sqlalchemy import select

from app.auth.tokens import create_access_token

SAMPLE_DATA = Path(__file__).parents[3] / "sample-data"


async def _read(name: str) -> bytes:
    with open(SAMPLE_DATA / name, "rb") as f:
        return f.read()


async def _post(client: AsyncClient, token: str, files: list[tuple[str, bytes]]) -> dict:
    payload = [("files", (name, content, "text/csv")) for name, content in files]
    response = await client.post(
        "/api/v1/admin/import-guarani",
        headers={"Authorization": f"Bearer {token}"},
        files=payload,
    )
    return response


@pytest.mark.asyncio
async def test_import_guarani_broadcasts_iso_created_at(
    client: AsyncClient, admin_token: str, db_session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Regresión: el payload WS debe llevar created_at ISO (no str() de Python),
    si no los navegadores estrictos no lo parsean y el live update se pierde."""
    import re

    from app.observability.ws_manager import manager

    seen: list[dict] = []

    async def capture(message: dict) -> None:
        seen.append(message)

    monkeypatch.setattr(manager, "broadcast", capture)
    await _post(client, admin_token, [("carreras.csv", await _read("carreras.csv"))])
    assert seen
    for message in seen:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*", message["payload"]["created_at"])


@pytest.mark.asyncio
async def test_import_guarani_rejects_non_admin(client: AsyncClient, test_user: User) -> None:
    token = create_access_token(test_user.id, test_user.role, test_user.email)
    response = await _post(client, token, [("carreras.csv", await _read("carreras.csv"))])
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_import_guarani_rejects_no_files(client: AsyncClient, admin_token: str) -> None:
    response = await client.post(
        "/api/v1/admin/import-guarani",
        headers={"Authorization": f"Bearer {admin_token}"},
        files=[],
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_import_guarani_accepts_returns_processing(client: AsyncClient, admin_token: str, db_session) -> None:
    response = await _post(client, admin_token, [("carreras.csv", await _read("carreras.csv"))])
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "processing", "count": 1}


@pytest.mark.asyncio
async def test_import_guarani_logs_ok_row_per_file(
    client: AsyncClient, admin_token: str, test_admin: User, db_session
) -> None:
    await _post(client, admin_token, [("carreras.csv", await _read("carreras.csv"))])

    events = (await db_session.execute(select(LogEvent).order_by(LogEvent.created_at))).scalars().all()
    assert len(events) == 1
    e = events[0]
    assert e.user_id == test_admin.id
    assert e.action == "import_guarani"
    assert e.status == "ok"
    assert e.details["sheet_type"] == "carreras"
    assert e.details["files"] == ["carreras.csv"]
    assert e.details["processed"] > 0
    assert e.details["skipped"] == 0
    assert e.details["error"] is None
    assert e.details["file_hash"] == sha256(await _read("carreras.csv")).hexdigest()
    assert e.details["preview"] is not None
    assert len(e.details["preview"]) == 6
    assert e.details["preview"] == (await _read("carreras.csv")).decode("utf-8").splitlines()[:6]
    assert e.details["preview_truncated"] is True
    assert e.details["uploader_email"] == test_admin.email
    assert e.details["skipped_sample"] == []


@pytest.mark.asyncio
async def test_import_guarani_logs_multiple_rows_per_file(
    client: AsyncClient, admin_token: str, test_admin: User, db_session
) -> None:
    files = [
        ("carreras.csv", await _read("carreras.csv")),
        ("materias.csv", await _read("materias.csv")),
        ("planes_tpi.csv", await _read("planes_tpi.csv")),
    ]
    await _post(client, admin_token, files)

    events = (await db_session.execute(select(LogEvent).order_by(LogEvent.created_at))).scalars().all()
    assert len(events) == 3
    types = [e.details["sheet_type"] for e in events]
    assert types == ["carreras", "materias", "planes_de_estudio"]
    assert all(e.status == "ok" for e in events)
    assert all(e.user_id == test_admin.id for e in events)


@pytest.mark.asyncio
async def test_import_guarani_logs_error_for_unknown_file(
    client: AsyncClient, admin_token: str, test_admin: User, db_session
) -> None:
    files = [
        ("carreras.csv", await _read("carreras.csv")),
        ("raro.csv", b"foo;bar;baz\n1;2;3\n"),
    ]
    await _post(client, admin_token, files)

    events = (await db_session.execute(select(LogEvent).order_by(LogEvent.created_at))).scalars().all()
    assert len(events) == 2
    ok = next(e for e in events if e.status == "ok")
    err = next(e for e in events if e.status == "error")
    assert ok.details["sheet_type"] == "carreras"
    assert err.details["sheet_type"] is None
    assert err.details["files"] == ["raro.csv"]
    assert err.details["error"] is not None


@pytest.mark.asyncio
async def test_import_guarani_logs_encoding_error(
    client: AsyncClient, admin_token: str, test_admin: User, db_session
) -> None:
    bad_content = "Códigò;Nombre;fecha\nA;Carrera Test;01/01/2000\n".encode("latin-1")
    files = [
        ("carreras.csv", await _read("carreras.csv")),
        ("latin1.csv", bad_content),
    ]
    await _post(client, admin_token, files)

    events = (await db_session.execute(select(LogEvent).order_by(LogEvent.created_at))).scalars().all()
    assert len(events) == 2
    err = next(e for e in events if e.status == "error")
    assert err.details["files"] == ["latin1.csv"]
    assert err.details["sheet_type"] is None
    assert "encoding" in err.details["error"]
    assert err.details["file_hash"] == sha256(bad_content).hexdigest()
    assert err.details["preview"] is None
    assert err.details["uploader_email"] == test_admin.email


@pytest.mark.asyncio
async def test_import_guarani_preserves_order_by_dependency(
    client: AsyncClient, admin_token: str, test_admin: User, db_session
) -> None:
    # Subimos en orden "desordenado": materias, carreras, planes.
    # El log debe reflejar el orden de dependencias: carreras, materias, planes.
    files = [
        ("materias.csv", await _read("materias.csv")),
        ("carreras.csv", await _read("carreras.csv")),
        ("planes_tpi.csv", await _read("planes_tpi.csv")),
    ]
    await _post(client, admin_token, files)

    events = (await db_session.execute(select(LogEvent).order_by(LogEvent.created_at))).scalars().all()
    types = [e.details["sheet_type"] for e in events]
    assert types == ["carreras", "materias", "planes_de_estudio"]


@pytest.mark.asyncio
async def test_import_guarani_oversized_file_excluded_from_count(
    client: AsyncClient, admin_token: str, test_admin: User, db_session
) -> None:
    big = b"x" * (11 * 1024 * 1024)
    files = [("carreras.csv", await _read("carreras.csv")), ("big.csv", big)]
    response = await _post(client, admin_token, files)
    assert response.status_code == 200
    body = response.json()
    # Oversized file is skipped at router level — only carreras counted.
    assert body["count"] == 1

    events = (await db_session.execute(select(LogEvent).order_by(LogEvent.created_at))).scalars().all()
    assert len(events) == 1
    assert events[0].status == "ok"
    assert events[0].details["sheet_type"] == "carreras"


@pytest.mark.asyncio
async def test_import_guarani_unexpected_exception_logged_and_continues(
    client: AsyncClient, admin_token: str, test_admin: User, db_session, monkeypatch
) -> None:
    from app.services.guarani_importer import GuaraniImporterService

    original_importar = GuaraniImporterService.importar
    call_count = 0

    async def flaky_importar(self, sheet_type, contents):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("boom inesperado")
        return await original_importar(self, sheet_type, contents)

    monkeypatch.setattr(GuaraniImporterService, "importar", flaky_importar)

    files = [
        ("carreras.csv", await _read("carreras.csv")),
        ("materias.csv", await _read("materias.csv")),
    ]
    await _post(client, admin_token, files)

    events = (await db_session.execute(select(LogEvent).order_by(LogEvent.created_at))).scalars().all()
    assert len(events) == 2
    err = next(e for e in events if e.status == "error")
    assert "error inesperado" in err.details["error"]
    ok = next(e for e in events if e.status == "ok")
    assert ok.details["sheet_type"] == "materias"
