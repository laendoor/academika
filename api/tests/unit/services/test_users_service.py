import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.errors import BusinessError, ConflictError, NotFoundError
from app.services.users import UserService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(session: AsyncMock) -> UserService:
    return UserService(session)


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "steve@unq.edu.ar"
    user.role = "director"
    user.is_active = True
    return user


@pytest.mark.asyncio
async def test_delete_success(service: UserService, session: AsyncMock, mock_user: MagicMock):
    session.get.return_value = mock_user
    await service.delete(mock_user.id, requester_id=uuid.uuid4())
    session.delete.assert_awaited_once_with(mock_user)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_self_forbidden(service: UserService, session: AsyncMock, mock_user: MagicMock):
    session.get.return_value = mock_user
    with pytest.raises(BusinessError):
        await service.delete(mock_user.id, requester_id=mock_user.id)
    session.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_not_found(service: UserService, session: AsyncMock):
    session.get.return_value = None
    with pytest.raises(NotFoundError):
        await service.delete(uuid.uuid4(), requester_id=uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_user_with_log_events_conflict(service: UserService, session: AsyncMock, mock_user: MagicMock):
    session.get.return_value = mock_user
    session.commit.side_effect = IntegrityError("DELETE", {}, Exception("fk violation"))
    with pytest.raises(ConflictError):
        await service.delete(mock_user.id, requester_id=uuid.uuid4())
    session.rollback.assert_awaited_once()
