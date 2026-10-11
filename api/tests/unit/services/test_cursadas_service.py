import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.cursadas import CursadaService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> CursadaService:
    return CursadaService.dep(session)


def _mock_list(session: AsyncMock, total: int | None, items: list) -> None:
    session.scalar.return_value = total
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    session.execute.return_value = result


# ── list_filtered ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_filtered_no_filters(service: CursadaService, session: AsyncMock):
    _mock_list(session, 5, ["c1"])
    assert await service.list_filtered() == (5, ["c1"])
    session.scalar.assert_awaited_once()
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_filtered_with_filters(service: CursadaService, session: AsyncMock):
    _mock_list(session, 1, ["c1"])
    alumno_id, materia_id = uuid.uuid4(), uuid.uuid4()
    assert await service.list_filtered(alumno_id=alumno_id, materia_id=materia_id, anio=2026, cuatrimestre="1C") == (
        1,
        ["c1"],
    )
    stmt = str(session.execute.await_args.args[0])
    assert "alumno_id" in stmt and "materia_id" in stmt and "anio" in stmt


@pytest.mark.asyncio
async def test_list_filtered_total_none_is_zero(service: CursadaService, session: AsyncMock):
    _mock_list(session, None, [])
    assert await service.list_filtered() == (0, [])
