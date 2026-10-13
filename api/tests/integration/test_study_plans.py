import pytest
from httpx import AsyncClient


async def _create_carrera(auth_client: AsyncClient, codigo: str = "TPI") -> dict:
    return (await auth_client.post("/api/v1/carreras", json={"nombre": codigo, "codigo": codigo})).json()


async def _create_materia(auth_client: AsyncClient, codigo: str) -> dict:
    return (await auth_client.post("/api/v1/materias", json={"nombre": codigo, "codigo": codigo})).json()


async def _create_plan(
    auth_client: AsyncClient, carrera_id: str, anio: int = 2015, materia_ids: list[str] | None = None
) -> dict:
    return (
        await auth_client.post(
            "/api/v1/planes",
            json={
                "carrera_id": carrera_id,
                "nombre": f"Plan {anio}",
                "anio": anio,
                "vigente": True,
                "materia_ids": materia_ids or [],
            },
        )
    ).json()


@pytest.mark.asyncio
async def test_get_plan_detail_with_materias(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client)
    mat1 = await _create_materia(auth_client, "MAT1")
    mat2 = await _create_materia(auth_client, "MAT2")
    plan = await _create_plan(auth_client, carrera["id"], materia_ids=[mat1["id"], mat2["id"]])

    response = await auth_client.get(f"/api/v1/planes/{plan['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["carrera_id"] == carrera["id"]
    assert data["carrera_nombre"] == "TPI"
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
