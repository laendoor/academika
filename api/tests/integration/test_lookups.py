import pytest
from httpx import AsyncClient

LOOKUP_PATHS = [
    "/api/v1/lookups/estado-academico",
    "/api/v1/lookups/estado-cursada",
    "/api/v1/lookups/tipo-cursada",
    "/api/v1/lookups/user-roles",
]


@pytest.mark.asyncio
async def test_list_user_roles(client: AsyncClient, admin_token: str) -> None:
    response = await client.get(
        "/api/v1/lookups/user-roles",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    items = response.json()
    assert {item["key"] for item in items} == {"admin", "director", "docente"}
    assert all({"key", "label"} <= set(item) for item in items)


@pytest.mark.asyncio
async def test_list_estado_academico(client: AsyncClient, admin_token: str) -> None:
    response = await client.get(
        "/api/v1/lookups/estado-academico",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    items = response.json()
    assert {item["key"] for item in items} == {"alumno_regular", "no_regular"}
    assert all(item["label"] for item in items)


@pytest.mark.asyncio
async def test_list_estado_cursada(client: AsyncClient, admin_token: str) -> None:
    response = await client.get(
        "/api/v1/lookups/estado-cursada",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    items = response.json()
    assert {item["key"] for item in items} == {
        "inscripto",
        "regular",
        "promocionado",
        "aprobado",
        "desaprobado",
        "pendiente_aprobacion",
    }
    assert all({"key", "code", "label"} <= set(item) for item in items)


@pytest.mark.asyncio
async def test_list_tipo_cursada(client: AsyncClient, admin_token: str) -> None:
    response = await client.get(
        "/api/v1/lookups/tipo-cursada",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    items = response.json()
    assert {item["key"] for item in items} == {"regular", "libre"}
    assert all(item["label"] for item in items)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", LOOKUP_PATHS)
async def test_lookups_require_auth(client: AsyncClient, path: str) -> None:
    response = await client.get(path)
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("path", LOOKUP_PATHS)
async def test_lookups_list_with_auth(client: AsyncClient, admin_token: str, path: str) -> None:
    response = await client.get(
        path,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
