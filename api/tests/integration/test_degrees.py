import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_degree(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/carreras", json={"name": "Tecnicatura en Programación Informática", "code": "TPI"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "TPI"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_degrees(client: AsyncClient) -> None:
    await client.post("/api/v1/carreras", json={"name": "TPI", "code": "TPI"})
    await client.post("/api/v1/carreras", json={"name": "Licenciatura en Informática", "code": "LI"})
    response = await client.get("/api/v1/carreras")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_degree_by_id(client: AsyncClient) -> None:
    created = (await client.post("/api/v1/carreras", json={"name": "TPI", "code": "TPI"})).json()
    response = await client.get(f"/api/v1/carreras/{created['id']}")
    assert response.status_code == 200
    assert response.json()["code"] == "TPI"


@pytest.mark.asyncio
async def test_get_degree_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/carreras/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_degree(client: AsyncClient) -> None:
    created = (await client.post("/api/v1/carreras", json={"name": "TPI", "code": "TPI"})).json()
    response = await client.put(f"/api/v1/carreras/{created['id']}", json={"name": "TPI actualizada"})
    assert response.status_code == 200
    assert response.json()["name"] == "TPI actualizada"


@pytest.mark.asyncio
async def test_delete_degree(client: AsyncClient) -> None:
    created = (await client.post("/api/v1/carreras", json={"name": "TPI", "code": "TPI"})).json()
    response = await client.delete(f"/api/v1/carreras/{created['id']}")
    assert response.status_code == 204
    assert (await client.get(f"/api/v1/carreras/{created['id']}")).status_code == 404


@pytest.mark.asyncio
async def test_create_degree_duplicate_code(client: AsyncClient) -> None:
    await client.post("/api/v1/carreras", json={"name": "TPI", "code": "TPI"})
    response = await client.post("/api/v1/carreras", json={"name": "Otra", "code": "TPI"})
    assert response.status_code == 409
