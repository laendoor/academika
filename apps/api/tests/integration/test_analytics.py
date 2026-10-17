import pytest
from httpx import AsyncClient


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_metricas_requiere_auth(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/analytics")).status_code == 401


@pytest.mark.asyncio
async def test_list_metricas_incluye_smoke(client: AsyncClient, admin_token: str) -> None:
    response = await client.get("/api/v1/analytics", headers=_auth(admin_token))
    assert response.status_code == 200
    assert {item["key"] for item in response.json()} >= {"smoke"}


@pytest.mark.asyncio
async def test_run_smoke_end_to_end(client: AsyncClient, admin_token: str) -> None:
    response = await client.get("/api/v1/analytics/smoke", headers=_auth(admin_token))
    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_run_desconocida_404(client: AsyncClient, admin_token: str) -> None:
    response = await client.get("/api/v1/analytics/no-existe", headers=_auth(admin_token))
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_docente_sin_acceso(client: AsyncClient, docente_token: str) -> None:
    assert (await client.get("/api/v1/analytics", headers=_auth(docente_token))).status_code == 403
    assert (await client.get("/api/v1/analytics/smoke", headers=_auth(docente_token))).status_code == 403
