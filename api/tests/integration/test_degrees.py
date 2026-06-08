import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_carrera(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/carreras", json={"nombre": "Tecnicatura en Programación Informática", "codigo": "TPI"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["codigo"] == "TPI"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_carreras(client: AsyncClient) -> None:
    await client.post("/api/v1/carreras", json={"nombre": "TPI", "codigo": "TPI"})
    await client.post("/api/v1/carreras", json={"nombre": "Licenciatura en Informática", "codigo": "LI"})
    response = await client.get("/api/v1/carreras")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_carrera_by_id(client: AsyncClient) -> None:
    created = (await client.post("/api/v1/carreras", json={"nombre": "TPI", "codigo": "TPI"})).json()
    response = await client.get(f"/api/v1/carreras/{created['id']}")
    assert response.status_code == 200
    assert response.json()["codigo"] == "TPI"


@pytest.mark.asyncio
async def test_get_carrera_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/carreras/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
