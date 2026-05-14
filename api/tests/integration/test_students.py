import pytest
from httpx import AsyncClient


async def _create_degree(client: AsyncClient, code: str = "TPI") -> dict:
    return (await client.post("/api/v1/carreras", json={"name": code, "code": code})).json()


@pytest.mark.asyncio
async def test_create_student(client: AsyncClient) -> None:
    degree = await _create_degree(client)
    response = await client.post(
        "/api/v1/alumnos",
        json={
            "first_name": "Ana",
            "last_name": "García",
            "doc_id": "12345678",
            "degree_id": degree["id"],
            "academic_status": "alumno_regular",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["doc_id"] == "12345678"
    assert data["degree_id"] == degree["id"]


@pytest.mark.asyncio
async def test_list_students(client: AsyncClient) -> None:
    degree = await _create_degree(client)
    for doc_id in ["11111111", "22222222"]:
        await client.post(
            "/api/v1/alumnos",
            json={
                "first_name": "x", "last_name": "x", "doc_id": doc_id,
                "degree_id": degree["id"], "academic_status": "alumno_regular",
            },
        )
    response = await client.get("/api/v1/alumnos")
    assert response.json()["total"] == 2


@pytest.mark.asyncio
async def test_get_student_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/alumnos/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_student_invalid_degree(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/alumnos",
        json={
            "first_name": "Ana",
            "last_name": "García",
            "doc_id": "12345678",
            "degree_id": "00000000-0000-0000-0000-000000000000",
            "academic_status": "alumno_regular",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_student_duplicate_doc_id(client: AsyncClient) -> None:
    degree = await _create_degree(client)
    payload = {
        "first_name": "x", "last_name": "x", "doc_id": "99999999",
        "degree_id": degree["id"], "academic_status": "alumno_regular",
    }
    await client.post("/api/v1/alumnos", json=payload)
    response = await client.post("/api/v1/alumnos", json=payload)
    assert response.status_code == 409
