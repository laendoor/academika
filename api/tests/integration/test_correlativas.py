import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.models.correlativa import Correlativa
from app.models.materia import Materia


@pytest.mark.asyncio
async def test_list_correlativas_expanded(auth_client: AsyncClient, db_session: AsyncSession) -> None:
    mat = Materia(id=generate_uuid(), nombre="Análisis I", codigo="ANA1")
    req = Materia(id=generate_uuid(), nombre="Álgebra", codigo="ALG")
    db_session.add_all([mat, req, Correlativa(materia_id=mat.id, requisito_id=req.id, es_obligatoria=True)])
    await db_session.commit()

    response = await auth_client.get("/api/v1/correlativas")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    item = data["items"][0]
    assert item["materia"] == {"id": str(mat.id), "codigo": "ANA1", "nombre": "Análisis I"}
    assert item["requisito"] == {"id": str(req.id), "codigo": "ALG", "nombre": "Álgebra"}
    assert item["es_obligatoria"] is True


@pytest.mark.asyncio
async def test_list_correlativas_filter_by_materia(auth_client: AsyncClient, db_session: AsyncSession) -> None:
    mat_a = Materia(id=generate_uuid(), nombre="A", codigo="A1")
    mat_b = Materia(id=generate_uuid(), nombre="B", codigo="B1")
    req = Materia(id=generate_uuid(), nombre="R", codigo="R1")
    db_session.add_all(
        [
            mat_a,
            mat_b,
            req,
            Correlativa(materia_id=mat_a.id, requisito_id=req.id, es_obligatoria=True),
            Correlativa(materia_id=mat_b.id, requisito_id=req.id, es_obligatoria=False),
        ]
    )
    await db_session.commit()

    response = await auth_client.get(f"/api/v1/correlativas?materia_id={mat_b.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["materia"]["codigo"] == "B1"
    assert data["items"][0]["es_obligatoria"] is False


@pytest.mark.asyncio
async def test_list_correlativas_empty(auth_client: AsyncClient) -> None:
    response = await auth_client.get("/api/v1/correlativas")
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}
