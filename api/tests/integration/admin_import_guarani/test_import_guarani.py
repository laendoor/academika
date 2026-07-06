from pathlib import Path

import pytest
import sqlalchemy as sa
from httpx import AsyncClient

from app.auth.tokens import create_access_token
from app.models.carrera import Carrera
from app.models.user import User

SAMPLE_DATA = Path(__file__).parents[3] / "sample-data"


@pytest.mark.asyncio
async def test_import_guarani_rejects_non_admin(client: AsyncClient, test_user: User) -> None:
    token = create_access_token(test_user.id, test_user.role, test_user.email)
    with open(SAMPLE_DATA / "carreras.csv", "rb") as f:
        response = await client.post(
            "/api/v1/admin/import-guarani",
            headers={"Authorization": f"Bearer {token}"},
            files=[("files", ("carreras.csv", f.read(), "text/csv"))],
        )
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
async def test_import_guarani_detects_and_processes_carreras(client: AsyncClient, admin_token: str, db_session) -> None:
    with open(SAMPLE_DATA / "carreras.csv", "rb") as f:
        response = await client.post(
            "/api/v1/admin/import-guarani",
            headers={"Authorization": f"Bearer {admin_token}"},
            files=[("files", ("carreras.csv", f.read(), "text/csv"))],
        )
    assert response.status_code == 200
    body = response.json()
    assert body["errors"] == []
    assert len(body["results"]) == 1
    r = body["results"][0]
    assert r["type"] == "carreras"
    assert r["processed"] > 0
    assert r["skipped"] == 0

    carreras = (await db_session.execute(sa.select(Carrera))).scalars().all()
    assert len(carreras) == r["processed"]


@pytest.mark.asyncio
async def test_import_guarani_multiple_types_respects_order_and_results(client: AsyncClient, admin_token: str) -> None:
    filenames = ["carreras.csv", "planes_tpi.csv", "materias.csv"]
    files_payload = []
    for name in filenames:
        with open(SAMPLE_DATA / name, "rb") as f:
            files_payload.append(("files", (name, f.read(), "text/csv")))

    response = await client.post(
        "/api/v1/admin/import-guarani",
        headers={"Authorization": f"Bearer {admin_token}"},
        files=files_payload,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["errors"] == []
    detected_types = {r["type"] for r in body["results"]}
    assert detected_types == {"carreras", "planes_de_estudio", "materias"}


@pytest.mark.asyncio
async def test_import_guarani_reports_unknown_file_in_errors(client: AsyncClient, admin_token: str) -> None:
    with open(SAMPLE_DATA / "carreras.csv", "rb") as f_ok:
        ok_content = f_ok.read()
    bad_content = b"foo;bar;baz\n1;2;3\n"
    files_payload = [
        ("files", ("carreras.csv", ok_content, "text/csv")),
        ("files", ("raro.csv", bad_content, "text/csv")),
    ]
    response = await client.post(
        "/api/v1/admin/import-guarani",
        headers={"Authorization": f"Bearer {admin_token}"},
        files=files_payload,
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["errors"]) == 1
    assert body["errors"][0]["file"] == "raro.csv"
    assert len(body["results"]) == 1
    assert body["results"][0]["type"] == "carreras"
