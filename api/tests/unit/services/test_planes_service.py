import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.errors import ConflictError, NotFoundError
from app.schemas.planes_de_estudio import PlanDeEstudioCreate, PlanDeEstudioUpdate
from app.services.planes_de_estudio import PlanDeEstudioService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> PlanDeEstudioService:
    return PlanDeEstudioService.dep(session)


@pytest.fixture
def mock_plan() -> MagicMock:
    plan = MagicMock()
    plan.id = uuid.uuid4()
    return plan


def _make_create(**kwargs) -> PlanDeEstudioCreate:
    return PlanDeEstudioCreate(carrera_id=uuid.uuid4(), nombre="Plan", anio=2026, **kwargs)


# ── create ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_with_materias(service: PlanDeEstudioService, session: AsyncMock):
    data = _make_create(materia_ids=[uuid.uuid4(), uuid.uuid4()])
    instance = await service.create(data)
    assert instance.nombre == "Plan"
    session.flush.assert_awaited_once()
    assert session.execute.await_count == 2  # delete + insert en planes_materias
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_without_materias_skips_insert(service: PlanDeEstudioService, session: AsyncMock):
    await service.create(_make_create())
    session.execute.assert_awaited_once()  # solo delete


@pytest.mark.asyncio
async def test_create_conflict(service: PlanDeEstudioService, session: AsyncMock):
    session.flush.side_effect = IntegrityError("INSERT", {}, Exception("duplicate"))
    with pytest.raises(ConflictError):
        await service.create(_make_create())
    session.rollback.assert_awaited_once()


# ── update ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_with_materias(service: PlanDeEstudioService, session: AsyncMock, mock_plan: MagicMock):
    session.get.return_value = mock_plan
    data = PlanDeEstudioUpdate(nombre="Nuevo", materia_ids=[uuid.uuid4()])
    instance = await service.update(mock_plan.id, data)
    assert instance.nombre == "Nuevo"
    assert session.execute.await_count == 2
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_without_materias_skips_assoc(
    service: PlanDeEstudioService, session: AsyncMock, mock_plan: MagicMock
):
    session.get.return_value = mock_plan
    instance = await service.update(mock_plan.id, PlanDeEstudioUpdate(nombre="Nuevo"))
    assert instance.nombre == "Nuevo"
    session.execute.assert_not_awaited()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_not_found(service: PlanDeEstudioService, session: AsyncMock):
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        await service.update(uuid.uuid4(), PlanDeEstudioUpdate(nombre="Nuevo"))


@pytest.mark.asyncio
async def test_update_conflict(service: PlanDeEstudioService, session: AsyncMock, mock_plan: MagicMock):
    session.get.return_value = mock_plan
    session.commit.side_effect = IntegrityError("UPDATE", {}, Exception("duplicate"))
    with pytest.raises(ConflictError):
        await service.update(mock_plan.id, PlanDeEstudioUpdate(nombre="Nuevo"))
    session.rollback.assert_awaited_once()
