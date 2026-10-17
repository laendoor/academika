from unittest.mock import AsyncMock, patch

import pytest
from starlette.requests import Request

from app.errors import NotFoundError
from app.routers.analytics import list_metrics, run_metric


def _request(query_string: bytes = b"") -> Request:
    return Request({"type": "http", "query_string": query_string})


@pytest.mark.asyncio
async def test_list_incluye_smoke() -> None:
    result = await list_metrics()
    assert {m.key for m in result} >= {"smoke"}


@pytest.mark.asyncio
async def test_run_smoke_pasa_query_como_params() -> None:
    session = AsyncMock()
    assert await run_metric("smoke", _request(b"carrera=tpi"), session) == {"ok": True}
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_desconocida_404() -> None:
    with pytest.raises(NotFoundError) as exc_info:
        await run_metric("no-existe", _request(), AsyncMock())
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_run_params_repetidos_como_lista() -> None:
    session = AsyncMock()
    with patch("app.routers.analytics.analytika") as registry:
        metrica = AsyncMock()
        metrica.run.return_value = {"ok": True}
        registry.find_metric.return_value = metrica
        assert await run_metric("m", _request(b"a=1&a=2&b=3"), session) == {"ok": True}
        metrica.run.assert_awaited_once_with(session, {"a": ["1", "2"], "b": "3"})
