import pytest
from httpx import AsyncClient


async def _setup(auth_client: AsyncClient) -> dict:
    carrera = (await auth_client.post("/api/v1/carreras", json={"nombre": "TPI", "codigo": "TPI"})).json()
    materia = (await auth_client.post("/api/v1/materias", json={"nombre": "Intro", "codigo": "IP"})).json()
    alumno = (
        await auth_client.post("/api/v1/alumnos", json={"nombre": "Ana", "apellido": "García", "dni": "12345678"})
    ).json()
    return {"carrera": carrera, "materia": materia, "alumno": alumno}


def _cursada_payload(
    alumno_id: str, materia_id: str, carrera_id: str, anio: int = 2024, cuatrimestre: str = "1C"
) -> dict:
    return {
        "alumno_id": alumno_id,
        "materia_id": materia_id,
        "carrera_id": carrera_id,
        "anio": anio,
        "cuatrimestre": cuatrimestre,
        "tipo_cursada": "regular",
        "estado_cursada": "inscripto",
    }


@pytest.mark.asyncio
async def test_create_cursada(auth_client: AsyncClient) -> None:
    data = await _setup(auth_client)
    payload = _cursada_payload(data["alumno"]["id"], data["materia"]["id"], data["carrera"]["id"])
    response = await auth_client.post("/api/v1/cursadas", json=payload)
    assert response.status_code == 201
    assert response.json()["cuatrimestre"] == "1C"


@pytest.mark.asyncio
async def test_filter_by_alumno(auth_client: AsyncClient) -> None:
    data = await _setup(auth_client)
    payload = _cursada_payload(data["alumno"]["id"], data["materia"]["id"], data["carrera"]["id"])
    await auth_client.post("/api/v1/cursadas", json=payload)
    response = await auth_client.get("/api/v1/cursadas", params={"alumno_id": data["alumno"]["id"]})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["alumno_id"] == data["alumno"]["id"]


@pytest.mark.asyncio
async def test_filter_by_anio_and_cuatrimestre(auth_client: AsyncClient) -> None:
    data = await _setup(auth_client)
    a_id, m_id, c_id = data["alumno"]["id"], data["materia"]["id"], data["carrera"]["id"]
    await auth_client.post("/api/v1/cursadas", json=_cursada_payload(a_id, m_id, c_id, anio=2023, cuatrimestre="1C"))
    await auth_client.post("/api/v1/cursadas", json=_cursada_payload(a_id, m_id, c_id, anio=2024, cuatrimestre="2C"))
    response = await auth_client.get("/api/v1/cursadas", params={"anio": 2024, "cuatrimestre": "2C"})
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["anio"] == 2024


@pytest.mark.asyncio
async def test_update_cursada_estado(auth_client: AsyncClient) -> None:
    data = await _setup(auth_client)
    payload = _cursada_payload(data["alumno"]["id"], data["materia"]["id"], data["carrera"]["id"])
    created = (await auth_client.post("/api/v1/cursadas", json=payload)).json()
    response = await auth_client.put(f"/api/v1/cursadas/{created['id']}", json={"estado_cursada": "regular"})
    assert response.status_code == 200
    assert response.json()["estado_cursada"] == "regular"


@pytest.mark.asyncio
async def test_get_cursada_not_found(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/api/v1/cursadas/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
