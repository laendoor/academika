import pytest
from httpx import AsyncClient


async def _create_alumno(auth_client: AsyncClient, dni: str, apellido: str, nombre: str) -> dict:
    response = await auth_client.post("/api/v1/alumnos", json={"nombre": nombre, "apellido": apellido, "dni": dni})
    assert response.status_code == 201
    return response.json()


async def _create_materia(auth_client: AsyncClient, codigo: str, nombre: str, sigla: str | None = None) -> dict:
    response = await auth_client.post("/api/v1/materias", json={"nombre": nombre, "codigo": codigo, "sigla": sigla})
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_search_alumnos_ignores_accents_case_and_enye(auth_client: AsyncClient) -> None:
    await _create_alumno(auth_client, dni="33333333", apellido="Núñez", nombre="Lucía")

    for q in ("luci", "LUCÍA", "nunez", "NÚÑEZ"):
        response = await auth_client.get("/api/v1/alumnos/search", params={"q": q})
        assert response.status_code == 200
        hits = response.json()
        assert len(hits) == 1, q
        assert hits[0]["label"] == "Núñez, Lucía · DNI 33333333"
        assert hits[0]["term"] == "Núñez Lucía"


@pytest.mark.asyncio
async def test_search_alumnos_matches_tokens_in_any_order(auth_client: AsyncClient) -> None:
    await _create_alumno(auth_client, dni="44444444", apellido="Fernández", nombre="Ana Lucía")
    await _create_alumno(auth_client, dni="55555555", apellido="Fernández", nombre="Bruno")

    for q in ("luci fernandez", "fernandez luci"):
        hits = (await auth_client.get("/api/v1/alumnos/search", params={"q": q})).json()
        assert [h["label"] for h in hits] == ["Fernández, Ana Lucía · DNI 44444444"], q


@pytest.mark.asyncio
async def test_search_alumnos_by_dni(auth_client: AsyncClient) -> None:
    await _create_alumno(auth_client, dni="66666666", apellido="Pérez", nombre="Ana")

    hits = (await auth_client.get("/api/v1/alumnos/search", params={"q": "66666666"})).json()

    assert len(hits) == 1
    assert hits[0]["label"].startswith("Pérez, Ana")


@pytest.mark.asyncio
async def test_search_respects_limit(auth_client: AsyncClient) -> None:
    for i in range(3):
        await _create_alumno(auth_client, dni=f"7000000{i}", apellido="Gómez", nombre=f"Ana {i}")

    hits = (await auth_client.get("/api/v1/alumnos/search", params={"q": "gomez", "limit": 2})).json()

    assert len(hits) == 2


@pytest.mark.asyncio
async def test_search_materias_ignores_accents(auth_client: AsyncClient) -> None:
    await _create_materia(auth_client, codigo="AM", nombre="Análisis Matemático", sigla="AM")

    for q in ("analisis", "MATEMATICO", "análi"):
        hits = (await auth_client.get("/api/v1/materias/search", params={"q": q})).json()
        assert len(hits) == 1, q
        assert hits[0]["label"] == "AM — Análisis Matemático"
        assert hits[0]["term"] == "Análisis Matemático"


@pytest.mark.asyncio
async def test_search_without_results(auth_client: AsyncClient) -> None:
    await _create_alumno(auth_client, dni="88888888", apellido="García", nombre="Ana")

    assert (await auth_client.get("/api/v1/alumnos/search", params={"q": "zzz"})).json() == []


@pytest.mark.asyncio
async def test_search_requires_auth(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/alumnos/search", params={"q": "ana"})).status_code == 401
    assert (await client.get("/api/v1/materias/search", params={"q": "ana"})).status_code == 401


@pytest.mark.asyncio
async def test_search_rejects_queries_shorter_than_two_chars(auth_client: AsyncClient) -> None:
    for q in ("", "a"):
        assert (await auth_client.get("/api/v1/alumnos/search", params={"q": q})).status_code == 422, q


@pytest.mark.asyncio
async def test_search_with_only_spaces_returns_no_hits(auth_client: AsyncClient) -> None:
    await _create_alumno(auth_client, dni="99999999", apellido="García", nombre="Ana")

    response = await auth_client.get("/api/v1/alumnos/search", params={"q": "   "})

    assert response.status_code == 200
    assert response.json() == []
