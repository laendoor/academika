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


@pytest.mark.asyncio
async def test_import_guarani_encoding_invalid_no_aborts_lote(client: AsyncClient, admin_token: str) -> None:
    """Archivo con encoding Latin-1 + archivo válido: el inválido entra en errors[],
    el válido se procesa. Verifica A1 (catch amplio en detección)."""
    with open(SAMPLE_DATA / "carreras.csv", "rb") as f_ok:
        ok_content = f_ok.read()
    # Header con 'á' en Latin-1 (0xE1). UTF-8 lo decodificaría como 0xC3 0xA1 —
    # cuando read_headers abre con encoding="utf-8", 0xE1 standalone tronar UnicodeDecodeError.
    bad_content = "Códigò;Nombre;fecha\nA;Carrera Test;01/01/2000\n".encode("latin-1")
    files_payload = [
        ("files", ("carreras.csv", ok_content, "text/csv")),
        ("files", ("latin1.csv", bad_content, "text/csv")),
    ]
    response = await client.post(
        "/api/v1/admin/import-guarani",
        headers={"Authorization": f"Bearer {admin_token}"},
        files=files_payload,
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["errors"]) == 1
    assert "latin1.csv" in body["errors"][0]["file"]
    assert len(body["results"]) == 1
    assert body["results"][0]["type"] == "carreras"


@pytest.mark.asyncio
async def test_import_guarani_type_failure_reported_continues_lote(client: AsyncClient, admin_token: str) -> None:
    """A2: subimos carreras (válido, UTF-8) + un CSV detectado como MATERIAS
    pero cuyo parseo truena por encoding Latin-1 (parse_courses → parse_csv →
    open con UTF-8 → UnicodeDecodeError). Verifica que importar_carreras procesa
    e importar_materias cae en errors[] como '(materias)', sin abortar el lote."""
    with open(SAMPLE_DATA / "carreras.csv", "rb") as f_carreras:
        carreras_content = f_carreras.read()
    # 5 cols, segundo valor entero ('2010') → detect_type identifica MATERIAS.
    # Pero con 'á' (Latin-1) en col 4 → UnicodeDecodeError cuando parser abre con UTF-8.
    bad_materias = "P;2010;1035;Matemática;mm\n".encode("latin-1")
    files_payload = [
        ("files", ("carreras.csv", carreras_content, "text/csv")),
        ("files", ("materias_bad.csv", bad_materias, "text/csv")),
    ]
    response = await client.post(
        "/api/v1/admin/import-guarani",
        headers={"Authorization": f"Bearer {admin_token}"},
        files=files_payload,
    )
    assert response.status_code == 200
    body = response.json()
    # carreras procesa normalmente
    assert any(r["type"] == "carreras" for r in body["results"])
    # materias_bad cae en errors como (materias) — A2 catch per-tipo en _process_in_order
    materias_error = [e for e in body["errors"] if "materias" in e["file"]]
    assert len(materias_error) == 1
