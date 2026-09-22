import pytest
from httpx import AsyncClient

_MISSING_ID = "00000000-0000-0000-0000-000000000000"

CRUD_ENDPOINTS = [
    ("GET", "/api/v1/carreras"),
    ("GET", "/api/v1/carreras/{id}"),
    ("POST", "/api/v1/carreras"),
    ("PUT", "/api/v1/carreras/{id}"),
    ("DELETE", "/api/v1/carreras/{id}"),
    ("GET", "/api/v1/materias"),
    ("GET", "/api/v1/materias/{id}"),
    ("POST", "/api/v1/materias"),
    ("PUT", "/api/v1/materias/{id}"),
    ("DELETE", "/api/v1/materias/{id}"),
    ("GET", "/api/v1/planes"),
    ("GET", "/api/v1/planes/{id}"),
    ("POST", "/api/v1/planes"),
    ("PUT", "/api/v1/planes/{id}"),
    ("DELETE", "/api/v1/planes/{id}"),
    ("GET", "/api/v1/alumnos"),
    ("GET", "/api/v1/alumnos/{id}"),
    ("POST", "/api/v1/alumnos"),
    ("PUT", "/api/v1/alumnos/{id}"),
    ("DELETE", "/api/v1/alumnos/{id}"),
    ("GET", "/api/v1/alumnos/{id}/carreras"),
    ("POST", "/api/v1/alumnos/{id}/carreras"),
    ("GET", "/api/v1/cursadas"),
    ("GET", "/api/v1/cursadas/{id}"),
    ("POST", "/api/v1/cursadas"),
    ("PUT", "/api/v1/cursadas/{id}"),
    ("DELETE", "/api/v1/cursadas/{id}"),
]


def _path(path: str) -> str:
    return path.replace("{id}", _MISSING_ID)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
@pytest.mark.parametrize(("method", "path"), CRUD_ENDPOINTS)
async def test_crud_requires_auth(client: AsyncClient, method: str, path: str) -> None:
    response = await client.request(method, _path(path))
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(("method", "path"), CRUD_ENDPOINTS)
async def test_crud_forbidden_for_docente(client: AsyncClient, docente_token: str, method: str, path: str) -> None:
    response = await client.request(method, _path(path), headers=_auth(docente_token))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_crud_allows_admin_read(client: AsyncClient, admin_token: str) -> None:
    response = await client.get("/api/v1/carreras", headers=_auth(admin_token))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crud_allows_admin_write(client: AsyncClient, admin_token: str) -> None:
    response = await client.post(
        "/api/v1/carreras", json={"nombre": "TPI", "codigo": "TPI"}, headers=_auth(admin_token)
    )
    assert response.status_code == 201
