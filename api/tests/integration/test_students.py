import pytest
from httpx import AsyncClient


async def _create_carrera(client: AsyncClient, codigo: str = "TPI") -> dict:
    return (await client.post("/api/v1/carreras", json={"nombre": codigo, "codigo": codigo})).json()


async def _create_plan(client: AsyncClient, carrera_id: str, anio: int = 2015) -> dict:
    return (
        await client.post(
            "/api/v1/planes",
            json={"carrera_id": carrera_id, "nombre": f"Plan {anio}", "anio": anio, "vigente": True},
        )
    ).json()


async def _create_alumno(client: AsyncClient, dni: str = "12345678") -> dict:
    return (await client.post("/api/v1/alumnos", json={"nombre": "Ana", "apellido": "García", "dni": dni})).json()


@pytest.mark.asyncio
async def test_create_alumno(client: AsyncClient) -> None:
    response = await client.post("/api/v1/alumnos", json={"nombre": "Ana", "apellido": "García", "dni": "12345678"})
    assert response.status_code == 201
    data = response.json()
    assert data["dni"] == "12345678"
    assert "carrera_id" not in data


@pytest.mark.asyncio
async def test_list_alumnos(client: AsyncClient) -> None:
    for dni in ["11111111", "22222222"]:
        await client.post("/api/v1/alumnos", json={"nombre": "x", "apellido": "x", "dni": dni})
    response = await client.get("/api/v1/alumnos")
    assert response.json()["total"] == 2


@pytest.mark.asyncio
async def test_get_alumno_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/alumnos/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_carrera_a_alumno(client: AsyncClient) -> None:
    carrera = await _create_carrera(client)
    plan = await _create_plan(client, carrera["id"])
    alumno = await _create_alumno(client)
    response = await client.post(
        f"/api/v1/alumnos/{alumno['id']}/carreras",
        json={"plan_id": plan["id"], "estado_academico": "alumno_regular"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["plan_id"] == plan["id"]
    assert data["estado_academico"] == "alumno_regular"


@pytest.mark.asyncio
async def test_list_carreras_de_alumno(client: AsyncClient) -> None:
    carrera1 = await _create_carrera(client, codigo="TPI")
    carrera2 = await _create_carrera(client, codigo="LI")
    plan1 = await _create_plan(client, carrera1["id"], anio=2015)
    plan2 = await _create_plan(client, carrera2["id"], anio=2018)
    alumno = await _create_alumno(client)
    for plan in [plan1, plan2]:
        await client.post(
            f"/api/v1/alumnos/{alumno['id']}/carreras",
            json={"plan_id": plan["id"], "estado_academico": "alumno_regular"},
        )
    response = await client.get(f"/api/v1/alumnos/{alumno['id']}/carreras")
    assert response.status_code == 200
    assert len(response.json()) == 2
