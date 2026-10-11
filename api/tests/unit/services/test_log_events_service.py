from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.log_events import LogEventService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> LogEventService:
    return LogEventService.dep(session)


# ── list_import_guarani ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_import_guarani_success(service: LogEventService, session: AsyncMock):
    session.scalar.return_value = 2
    result = MagicMock()
    result.scalars.return_value.all.return_value = ["e1", "e2"]
    session.execute.return_value = result
    assert await service.list_import_guarani() == (2, ["e1", "e2"])
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_import_guarani_empty(service: LogEventService, session: AsyncMock):
    session.scalar.return_value = None
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result
    assert await service.list_import_guarani(skip=10, limit=5) == (0, [])
