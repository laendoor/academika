import pytest
from httpx import AsyncClient


async def _create_carrera(auth_client: AsyncClient, codigo: str = "TPI") -> dict:
    response = await auth_client.post("/api/v1/carreras", json={"nombre": f"Carrera {codigo}", "codigo": codigo})
    assert response.status_code == 201
    return response.json()


async def _create_materia(auth_client: AsyncClient, codigo: str) -> dict:
    response = await auth_client.post("/api/v1/materias", json={"nombre": codigo, "codigo": codigo})
    assert response.status_code == 201
    return response.json()


async def _create_plan(
    auth_client: AsyncClient, carrera_id: str, anio: int = 2015, materia_ids: list[str] | None = None
) -> dict:
    response = await auth_client.post(
        "/api/v1/planes",
        json={
            "carrera_id": carrera_id,
            "nombre": f"Plan {anio}",
            "anio": anio,
            "vigente": True,
            "materia_ids": materia_ids or [],
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_get_plan_detail_with_materias(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client)
    mat2 = await _create_materia(auth_client, "MAT2")
    mat1 = await _create_materia(auth_client, "MAT1")
    plan = await _create_plan(auth_client, carrera["id"], materia_ids=[mat2["id"], mat1["id"]])

    response = await auth_client.get(f"/api/v1/planes/{plan['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["carrera_id"] == carrera["id"]
    assert data["carrera_nombre"] == "Carrera TPI"
    assert data["anio"] == 2015
    assert [m["codigo"] for m in data["materias"]] == ["MAT1", "MAT2"]


@pytest.mark.asyncio
async def test_get_plan_detail_not_found(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/api/v1/planes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_planes_filter_by_carrera(auth_client: AsyncClient) -> None:
    carrera1 = await _create_carrera(auth_client, codigo="TPI")
    carrera2 = await _create_carrera(auth_client, codigo="LI")
    await _create_plan(auth_client, carrera1["id"], anio=2015)
    await _create_plan(auth_client, carrera2["id"], anio=2018)

    response = await auth_client.get(f"/api/v1/planes?carrera_id={carrera1['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["anio"] == 2015
    assert data["items"][0]["carrera_nombre"] == "Carrera TPI"


@pytest.mark.asyncio
async def test_update_plan(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client)
    materia = await _create_materia(auth_client, "MAT1")
    plan = await _create_plan(auth_client, carrera["id"])

    response = await auth_client.put(
        f"/api/v1/planes/{plan['id']}",
        json={"nombre": "Plan Nuevo", "materia_ids": [materia["id"]]},
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Plan Nuevo"

    detail = (await auth_client.get(f"/api/v1/planes/{plan['id']}")).json()
    assert [m["codigo"] for m in detail["materias"]] == ["MAT1"]


@pytest.mark.asyncio
async def test_delete_plan(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client)
    plan = await _create_plan(auth_client, carrera["id"])

    response = await auth_client.delete(f"/api/v1/planes/{plan['id']}")
    assert response.status_code == 204

    response = await auth_client.get(f"/api/v1/planes/{plan['id']}")
    assert response.status_code == 404
