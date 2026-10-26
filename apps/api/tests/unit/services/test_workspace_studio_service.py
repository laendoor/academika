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


# ── list_cursadas ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_cursadas_no_filters(service: WorkspaceStudioService, session: AsyncMock):
    session.scalar.return_value = 4
    session.execute.return_value = _scalars_result(["c1"])
    assert await service.list_cursadas() == (4, ["c1"])
    assert "ORDER BY cursadas.anio DESC" in str(session.execute.await_args.args[0])


@pytest.mark.asyncio
async def test_list_cursadas_filters_reach_count_and_page(service: WorkspaceStudioService, session: AsyncMock):
    import uuid

    session.scalar.return_value = 1
    session.execute.return_value = _scalars_result(["c1"])
    assert await service.list_cursadas(
        carrera_id=uuid.uuid4(),
        alumno="gar",
        materia="intro",
        anio=2024,
        cuatrimestre="1C",
        estado_cursada=["regular", "aprobado"],
        tipo_cursada="regular",
    ) == (1, ["c1"])

    count_stmt = str(session.scalar.await_args.args[0])
    page_stmt = str(session.execute.await_args.args[0])
    for stmt in (count_stmt, page_stmt):
        assert "carrera_id" in stmt
        assert "cursadas.anio" in stmt
        assert "cuatrimestre" in stmt
        assert "tipo_cursada" in stmt
        assert "alumnos" in stmt and "materias" in stmt
    assert "IN " in page_stmt and "inscripto" not in page_stmt


@pytest.mark.asyncio
async def test_list_cursadas_total_none_is_zero(service: WorkspaceStudioService, session: AsyncMock):
    session.scalar.return_value = None
    session.execute.return_value = _scalars_result([])
    assert await service.list_cursadas() == (0, [])


# ── get_estudiante_detalle ────────────────────────────────────────────────────


def _single_result(item) -> MagicMock:
    result = MagicMock()
    result.scalar_one_or_none.return_value = item
    return result


@pytest.mark.asyncio
async def test_get_estudiante_detalle_returns_carreras_and_historial(
    service: WorkspaceStudioService, session: AsyncMock
):
    import uuid

    session.execute.side_effect = [_single_result("a1"), _scalars_result(["c1", "c2"])]
    assert await service.get_estudiante_detalle(uuid.uuid4()) == ("a1", ["c1", "c2"])
    session.scalar.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_estudiante_detalle_not_found(service: WorkspaceStudioService, session: AsyncMock):
    import uuid

    from app.errors import NotFoundError

    session.execute.return_value = _single_result(None)
    with pytest.raises(NotFoundError):
        await service.get_estudiante_detalle(uuid.uuid4())
