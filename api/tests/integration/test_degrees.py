import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_carrera(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/carreras", json={"nombre": "Tecnicatura en Programación Informática", "codigo": "TPI"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["codigo"] == "TPI"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_carreras(auth_client: AsyncClient) -> None:
    await auth_client.post("/api/v1/carreras", json={"nombre": "TPI", "codigo": "TPI"})
    await auth_client.post("/api/v1/carreras", json={"nombre": "Licenciatura en Informática", "codigo": "LI"})
    response = await auth_client.get("/api/v1/carreras")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_carrera_by_id(auth_client: AsyncClient) -> None:
    created = (await auth_client.post("/api/v1/carreras", json={"nombre": "TPI", "codigo": "TPI"})).json()
    response = await auth_client.get(f"/api/v1/carreras/{created['id']}")
    assert response.status_code == 200
    assert response.json()["codigo"] == "TPI"


@pytest.mark.asyncio
async def test_get_carrera_not_found(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/api/v1/carreras/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
