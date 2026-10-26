import pytest
from httpx import AsyncClient


async def _create_carrera(auth_client: AsyncClient, codigo: str = "TPI") -> dict:
    response = await auth_client.post("/api/v1/carreras", json={"nombre": f"Carrera {codigo}", "codigo": codigo})
    assert response.status_code == 201
    return response.json()


async def _create_materia(auth_client: AsyncClient, codigo: str = "IP") -> dict:
    response = await auth_client.post("/api/v1/materias", json={"nombre": f"Materia {codigo}", "codigo": codigo})
    assert response.status_code == 201
    return response.json()


async def _create_alumno(auth_client: AsyncClient, dni: str = "12345678", apellido: str = "García") -> dict:
    response = await auth_client.post("/api/v1/alumnos", json={"nombre": "Ana", "apellido": apellido, "dni": dni})
    assert response.status_code == 201
    return response.json()


async def _create_cursada(
    auth_client: AsyncClient,
    alumno_id: str,
    materia_id: str,
    carrera_id: str,
    anio: int = 2024,
    cuatrimestre: str = "1C",
    estado: str = "inscripto",
    tipo: str = "regular",
) -> dict:
    response = await auth_client.post(
        "/api/v1/cursadas",
        json={
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "carrera_id": carrera_id,
            "anio": anio,
            "cuatrimestre": cuatrimestre,
            "tipo_cursada": tipo,
            "estado_cursada": estado,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_list_cursadas_expands_references(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client)
    materia = await _create_materia(auth_client)
    alumno = await _create_alumno(auth_client)
    await _create_cursada(auth_client, alumno["id"], materia["id"], carrera["id"], anio=2023, cuatrimestre="2C")
    await _create_cursada(
        auth_client, alumno["id"], materia["id"], carrera["id"], anio=2024, cuatrimestre="1C", estado="regular"
    )

    response = await auth_client.get("/api/v1/workspace/cursadas")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    first = body["items"][0]
    assert first["anio"] == 2024
    assert first["alumno"] == {"id": alumno["id"], "nombre": "Ana", "apellido": "García", "legajo": None}
    assert first["materia"] == {"id": materia["id"], "codigo": "IP", "nombre": "Materia IP"}
    assert first["carrera"] == {"id": carrera["id"], "codigo": "TPI", "nombre": "Carrera TPI"}


@pytest.mark.asyncio
async def test_filter_by_estado_cursada_repeated(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client)
    materia = await _create_materia(auth_client)
    alumno = await _create_alumno(auth_client)
    await _create_cursada(auth_client, alumno["id"], materia["id"], carrera["id"], anio=2023, estado="inscripto")
    await _create_cursada(auth_client, alumno["id"], materia["id"], carrera["id"], anio=2024, estado="regular")
    await _create_cursada(auth_client, alumno["id"], materia["id"], carrera["id"], anio=2025, estado="aprobado")

    response = await auth_client.get(
        "/api/v1/workspace/cursadas",
        params=[("estado_cursada", "regular"), ("estado_cursada", "aprobado")],
    )

    estados = {item["estado_cursada"] for item in response.json()["items"]}
    assert estados == {"regular", "aprobado"}


@pytest.mark.asyncio
async def test_filter_by_carrera_alumno_materia(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client, codigo="TPI")
    otra_carrera = await _create_carrera(auth_client, codigo="TRI")
    materia = await _create_materia(auth_client, codigo="IP")
    otra_materia = await _create_materia(auth_client, codigo="AYED")
    alumno = await _create_alumno(auth_client, dni="11111111", apellido="García")
    otro_alumno = await _create_alumno(auth_client, dni="22222222", apellido="López")
    await _create_cursada(auth_client, alumno["id"], materia["id"], carrera["id"])
    await _create_cursada(auth_client, otro_alumno["id"], otra_materia["id"], otra_carrera["id"])

    assert (await auth_client.get("/api/v1/workspace/cursadas", params={"carrera_id": carrera["id"]})).json()[
        "total"
    ] == 1
    assert (await auth_client.get("/api/v1/workspace/cursadas", params={"alumno": "gar"})).json()["total"] == 1
    assert (await auth_client.get("/api/v1/workspace/cursadas", params={"alumno": "11111111"})).json()["total"] == 1
    assert (await auth_client.get("/api/v1/workspace/cursadas", params={"materia": "ayed"})).json()["items"][0][
        "materia"
    ]["codigo"] == "AYED"


@pytest.mark.asyncio
async def test_filter_by_anio_cuatrimestre_tipo(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client)
    materia = await _create_materia(auth_client)
    alumno = await _create_alumno(auth_client)
    await _create_cursada(auth_client, alumno["id"], materia["id"], carrera["id"], anio=2024, cuatrimestre="1C")
    await _create_cursada(
        auth_client,
        alumno["id"],
        materia["id"],
        carrera["id"],
        anio=2025,
        cuatrimestre="2C",
        estado="aprobado",
        tipo="libre",
    )

    response = await auth_client.get(
        "/api/v1/workspace/cursadas", params={"anio": 2025, "cuatrimestre": "2C", "tipo_cursada": "libre"}
    )

    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["tipo_cursada"] == "libre"


@pytest.mark.asyncio
async def test_estudiante_detalle_returns_carreras_and_historial(auth_client: AsyncClient) -> None:
    carrera = await _create_carrera(auth_client)
    plan = (
        await auth_client.post(
            "/api/v1/planes",
            json={"carrera_id": carrera["id"], "nombre": "Plan 2015", "anio": 2015, "vigente": True},
        )
    ).json()
    materia = await _create_materia(auth_client)
    alumno = await _create_alumno(auth_client)
    await auth_client.post(
        f"/api/v1/alumnos/{alumno['id']}/carreras",
        json={"plan_id": plan["id"], "estado_academico": "alumno_regular"},
    )
    await _create_cursada(auth_client, alumno["id"], materia["id"], carrera["id"], estado="aprobado")

    response = await auth_client.get(f"/api/v1/workspace/estudiantes/{alumno['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["apellido"] == "García"
    assert body["carreras"][0]["plan_nombre"] == "Plan 2015"
    assert body["carreras"][0]["carrera_nombre"] == "Carrera TPI"
    assert body["carreras"][0]["estado_academico"] == "alumno_regular"
    assert [c["estado_cursada"] for c in body["cursadas"]] == ["aprobado"]


@pytest.mark.asyncio
async def test_estudiante_detalle_not_found(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/api/v1/workspace/estudiantes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cursadas_requires_director_role(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/workspace/cursadas")).status_code == 401
