import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.errors import ConflictError, NotFoundError
from app.schemas.alumnos import AlumnoCarreraCreate
from app.services.alumnos import AlumnoService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> AlumnoService:
    return AlumnoService.dep(session)


@pytest.fixture
def mock_alumno() -> MagicMock:
    alumno = MagicMock()
    alumno.id = uuid.uuid4()
    return alumno


# ── get_carreras ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_carreras_success(service: AlumnoService, session: AsyncMock, mock_alumno: MagicMock):
    session.get.return_value = mock_alumno
    result = MagicMock()
    result.scalars.return_value.all.return_value = ["c1", "c2"]
    session.execute.return_value = result
    assert await service.get_carreras(mock_alumno.id) == ["c1", "c2"]


@pytest.mark.asyncio
async def test_get_carreras_alumno_not_found(service: AlumnoService, session: AsyncMock):
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_carreras(uuid.uuid4())


# ── add_carrera ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_carrera_success(service: AlumnoService, session: AsyncMock, mock_alumno: MagicMock):
    session.get.return_value = mock_alumno
    data = AlumnoCarreraCreate(plan_id=uuid.uuid4(), estado_academico="alumno_regular")
    instance = await service.add_carrera(mock_alumno.id, data)
    assert instance.alumno_id == mock_alumno.id
    assert instance.plan_id == data.plan_id
    session.add.assert_called_once_with(instance)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_carrera_alumno_not_found(service: AlumnoService, session: AsyncMock):
    session.get.return_value = None
    data = AlumnoCarreraCreate(plan_id=uuid.uuid4(), estado_academico="alumno_regular")
    with pytest.raises(NotFoundError):
        await service.add_carrera(uuid.uuid4(), data)
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_add_carrera_conflict(service: AlumnoService, session: AsyncMock, mock_alumno: MagicMock):
    session.get.return_value = mock_alumno
    session.commit.side_effect = IntegrityError("INSERT", {}, Exception("duplicate"))
    data = AlumnoCarreraCreate(plan_id=uuid.uuid4(), estado_academico="alumno_regular")
    with pytest.raises(ConflictError):
        await service.add_carrera(mock_alumno.id, data)
    session.rollback.assert_awaited_once()
