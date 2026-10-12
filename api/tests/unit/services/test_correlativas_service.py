import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.correlativas import CorrelativaService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> CorrelativaService:
    return CorrelativaService.dep(session)


def _mock_list(session: AsyncMock, total: int | None, items: list) -> None:
    session.scalar.return_value = total
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    session.execute.return_value = result


# ── list_filtered ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_filtered_no_filters(service: CorrelativaService, session: AsyncMock):
    _mock_list(session, 3, ["c1"])
    assert await service.list_filtered() == (3, ["c1"])
    session.scalar.assert_awaited_once()
    session.execute.assert_awaited_once()
    assert "WHERE" not in str(session.execute.await_args.args[0])


@pytest.mark.asyncio
async def test_list_filtered_by_materia(service: CorrelativaService, session: AsyncMock):
    _mock_list(session, 1, ["c1"])
    assert await service.list_filtered(materia_id=uuid.uuid4()) == (1, ["c1"])
    assert "WHERE" in str(session.execute.await_args.args[0])


@pytest.mark.asyncio
async def test_list_filtered_total_none_is_zero(service: CorrelativaService, session: AsyncMock):
    _mock_list(session, None, [])
    assert await service.list_filtered() == (0, [])
