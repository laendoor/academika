from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.errors import ConflictError, NotFoundError
from app.models.setting import Setting
from app.schemas.settings import SettingUpdate
from app.services.settings import SettingService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> SettingService:
    return SettingService(session)


def _mock_execute(session: AsyncMock, scalars: list | None = None, scalar: Any = "unset") -> None:
    result = MagicMock()
    result.scalars.return_value.all.return_value = scalars or []
    if scalar != "unset":
        result.scalar_one_or_none.return_value = scalar
    session.execute.return_value = result


def _make_setting(key: str = "auth.allowed_domains", value: Any = None) -> Setting:
    return Setting(key=key, value=["@unq.edu.ar"] if value is None else value, description="test")


# ── list_all ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_all_ordered(service: SettingService, session: AsyncMock):
    _mock_execute(session, scalars=[_make_setting("b"), _make_setting("a")])
    settings = await service.list_all()
    assert [s.key for s in settings] == ["b", "a"]
    assert "ORDER BY" in str(session.execute.await_args.args[0])


# ── find/get by key ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_find_by_key_found(service: SettingService, session: AsyncMock):
    setting = _make_setting()
    _mock_execute(session, scalar=setting)
    assert await service.find_by_key("auth.allowed_domains") is setting


@pytest.mark.asyncio
async def test_find_by_key_missing(service: SettingService, session: AsyncMock):
    _mock_execute(session, scalar=None)
    assert await service.find_by_key("no.existe") is None


@pytest.mark.asyncio
async def test_get_by_key_missing_raises(service: SettingService, session: AsyncMock):
    _mock_execute(session, scalar=None)
    with pytest.raises(NotFoundError):
        await service.get_by_key("no.existe")


# ── update_value ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_value_success(service: SettingService, session: AsyncMock):
    _mock_execute(session, scalar=_make_setting())
    updated = await service.update_value("auth.allowed_domains", SettingUpdate(value=[]))
    assert updated.value == []
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_value_missing_raises(service: SettingService, session: AsyncMock):
    _mock_execute(session, scalar=None)
    with pytest.raises(NotFoundError):
        await service.update_value("no.existe", SettingUpdate(value=[]))
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_value_conflict(service: SettingService, session: AsyncMock):
    _mock_execute(session, scalar=_make_setting())
    session.commit.side_effect = IntegrityError("stmt", {}, Exception("boom"))
    with pytest.raises(ConflictError):
        await service.update_value("auth.allowed_domains", SettingUpdate(value=[]))
    session.rollback.assert_awaited_once()
