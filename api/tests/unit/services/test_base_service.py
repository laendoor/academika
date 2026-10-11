import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.errors import ConflictError, NotFoundError
from app.models.setting import Setting
from app.schemas.settings import SettingUpdate
from app.services.base import BaseService


class _SettingService(BaseService[Setting, SettingUpdate, SettingUpdate]):
    model = Setting


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> _SettingService:
    return _SettingService.dep(session)


# ── get_by_id ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_by_id_found(service: _SettingService, session: AsyncMock):
    setting = MagicMock()
    session.get.return_value = setting
    assert await service.get_by_id(uuid.uuid4()) is setting


@pytest.mark.asyncio
async def test_get_by_id_missing(service: _SettingService, session: AsyncMock):
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_by_id(uuid.uuid4())


# ── list ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_paginated(service: _SettingService, session: AsyncMock):
    session.scalar.return_value = 2
    result = MagicMock()
    result.scalars.return_value.all.return_value = ["s1"]
    session.execute.return_value = result
    assert await service.list(skip=1, limit=5) == (2, ["s1"])


# ── create ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_success(service: _SettingService, session: AsyncMock):
    instance = await service.create(SettingUpdate(value=["@unq.edu.ar"]))
    assert instance.value == ["@unq.edu.ar"]
    assert isinstance(instance.id, uuid.UUID)
    session.add.assert_called_once_with(instance)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_conflict(service: _SettingService, session: AsyncMock):
    session.commit.side_effect = IntegrityError("INSERT", {}, Exception("duplicate"))
    with pytest.raises(ConflictError):
        await service.create(SettingUpdate(value=[]))
    session.rollback.assert_awaited_once()


# ── update ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_success(service: _SettingService, session: AsyncMock):
    setting = Setting(key="k", value="old")
    session.get.return_value = setting
    updated = await service.update(uuid.uuid4(), SettingUpdate(value="new"))
    assert updated.value == "new"
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_conflict(service: _SettingService, session: AsyncMock):
    session.get.return_value = Setting(key="k", value="old")
    session.commit.side_effect = IntegrityError("UPDATE", {}, Exception("duplicate"))
    with pytest.raises(ConflictError):
        await service.update(uuid.uuid4(), SettingUpdate(value="new"))
    session.rollback.assert_awaited_once()


# ── delete ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_success(service: _SettingService, session: AsyncMock):
    setting = MagicMock()
    session.get.return_value = setting
    await service.delete(uuid.uuid4())
    session.delete.assert_awaited_once_with(setting)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_not_found(service: _SettingService, session: AsyncMock):
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        await service.delete(uuid.uuid4())
