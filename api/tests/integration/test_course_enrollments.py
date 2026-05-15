import pytest
from httpx import AsyncClient


async def _setup(client: AsyncClient) -> dict:
    degree = (await client.post("/api/v1/carreras", json={"name": "TPI", "code": "TPI"})).json()
    course = (await client.post("/api/v1/materias", json={"name": "Intro", "code": "IP"})).json()
    student = (await client.post(
        "/api/v1/alumnos",
        json={
            "first_name": "Ana", "last_name": "García", "doc_id": "12345678",
            "degree_id": degree["id"], "academic_status": "alumno_regular",
        },
    )).json()
    return {"degree": degree, "course": course, "student": student}


def _enrollment_payload(student_id: str, course_id: str, year: int = 2024, term: str = "1C") -> dict:
    return {
        "student_id": student_id,
        "course_id": course_id,
        "year": year,
        "term": term,
        "enrollment_type": "regular",
        "enrollment_status": "inscripto",
    }


@pytest.mark.asyncio
async def test_create_enrollment(client: AsyncClient) -> None:
    data = await _setup(client)
    payload = _enrollment_payload(data["student"]["id"], data["course"]["id"])
    response = await client.post("/api/v1/inscripciones", json=payload)
    assert response.status_code == 201
    assert response.json()["term"] == "1C"


@pytest.mark.asyncio
async def test_filter_by_student(client: AsyncClient) -> None:
    data = await _setup(client)
    payload = _enrollment_payload(data["student"]["id"], data["course"]["id"])
    await client.post("/api/v1/inscripciones", json=payload)
    response = await client.get("/api/v1/inscripciones", params={"student_id": data["student"]["id"]})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["student_id"] == data["student"]["id"]


@pytest.mark.asyncio
async def test_filter_by_year_and_term(client: AsyncClient) -> None:
    data = await _setup(client)
    s_id, c_id = data["student"]["id"], data["course"]["id"]
    await client.post("/api/v1/inscripciones", json=_enrollment_payload(s_id, c_id, year=2023, term="1C"))
    await client.post("/api/v1/inscripciones", json=_enrollment_payload(s_id, c_id, year=2024, term="2C"))
    response = await client.get("/api/v1/inscripciones", params={"year": 2024, "term": "2C"})
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["year"] == 2024


@pytest.mark.asyncio
async def test_update_enrollment_status(client: AsyncClient) -> None:
    data = await _setup(client)
    payload = _enrollment_payload(data["student"]["id"], data["course"]["id"])
    created = (await client.post("/api/v1/inscripciones", json=payload)).json()
    response = await client.put(
        f"/api/v1/inscripciones/{created['id']}", json={"enrollment_status": "regular"}
    )
    assert response.status_code == 200
    assert response.json()["enrollment_status"] == "regular"


@pytest.mark.asyncio
async def test_get_enrollment_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/inscripciones/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
