from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.workspace_studio import WorkspaceStudioService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> WorkspaceStudioService:
    return WorkspaceStudioService.dep(session)


def _ids_result(ids: list) -> MagicMock:
    result = MagicMock()
    result.__iter__.return_value = iter([(i,) for i in ids])
    return result


def _scalars_result(items: list) -> MagicMock:
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    return result


# ── list_estudiantes ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_estudiantes_empty_ids_short_circuits(service: WorkspaceStudioService, session: AsyncMock):
    session.scalar.return_value = 5
    session.execute.return_value = _ids_result([])
    assert await service.list_estudiantes() == (5, [])
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_estudiantes_with_ids(service: WorkspaceStudioService, session: AsyncMock):
    import uuid

    session.scalar.return_value = 1
    session.execute.side_effect = [_ids_result([uuid.uuid4()]), _scalars_result(["a1"])]
    assert await service.list_estudiantes() == (1, ["a1"])
    assert session.execute.await_count == 2


@pytest.mark.asyncio
async def test_list_estudiantes_total_none_is_zero(service: WorkspaceStudioService, session: AsyncMock):
    session.scalar.return_value = None
    session.execute.return_value = _ids_result([])
    assert await service.list_estudiantes() == (0, [])


# ── list_materias ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_materias_success(service: WorkspaceStudioService, session: AsyncMock):
    session.scalar.return_value = 3
    session.execute.return_value = _scalars_result(["m1"])
    assert await service.list_materias() == (3, ["m1"])
    assert "ORDER BY" in str(session.execute.await_args.args[0])


@pytest.mark.asyncio
async def test_list_estudiantes_with_filters(service: WorkspaceStudioService, session: AsyncMock):
    import uuid

    session.scalar.return_value = 1
    session.execute.side_effect = [_ids_result([uuid.uuid4()]), _scalars_result(["a1"])]
    total, items = await service.list_estudiantes(carrera_id=uuid.uuid4(), estado_academico="alumno_regular")
    assert (total, items) == (1, ["a1"])
    stmt = str(session.execute.await_args_list[0].args[0])
    assert "carrera_id" in stmt and "estado_academico" in stmt
