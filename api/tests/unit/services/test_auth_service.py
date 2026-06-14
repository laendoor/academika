import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.auth.errors import InvalidCredentialsError, InvalidTokenError, UnauthorizedDomainError
from app.auth.password import hash_password
from app.auth.tokens import create_access_token, create_invite_token, create_refresh_token, create_reset_token
from app.errors import ConflictError
from app.services.auth import AuthService
from app.services.users import UserService


@pytest.fixture
def session() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mail() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(session: AsyncMock, mail: MagicMock) -> AuthService:
    return AuthService(session, UserService(session), mail)


@pytest.fixture
def mock_user() -> MagicMock:
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = "steve@unq.edu.ar"
    user.hashed_password = hash_password("secreto123")
    user.role = "director"
    user.is_active = True
    return user


def _mock_execute(session: AsyncMock, return_value) -> None:
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
    session.execute.return_value = result


# ── login ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_success(service: AuthService, session: AsyncMock, mock_user: MagicMock):
    _mock_execute(session, mock_user)
    tokens = await service.login("steve@unq.edu.ar", "secreto123")
    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.mark.asyncio
async def test_login_wrong_domain(service: AuthService):
    with pytest.raises(UnauthorizedDomainError):
        await service.login("steve@gmail.com", "secreto123")


@pytest.mark.asyncio
async def test_login_user_not_found(service: AuthService, session: AsyncMock):
    _mock_execute(session, None)
    with pytest.raises(InvalidCredentialsError):
        await service.login("nadie@unq.edu.ar", "secreto123")


@pytest.mark.asyncio
async def test_login_wrong_password(service: AuthService, session: AsyncMock, mock_user: MagicMock):
    _mock_execute(session, mock_user)
    with pytest.raises(InvalidCredentialsError):
        await service.login("steve@unq.edu.ar", "incorrect")


@pytest.mark.asyncio
async def test_login_inactive_user(service: AuthService, session: AsyncMock):
    # El WHERE User.is_active en la query hace que la DB no devuelva usuarios inactivos
    _mock_execute(session, None)
    with pytest.raises(InvalidCredentialsError):
        await service.login("steve@unq.edu.ar", "secreto123")


# ── refresh ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_success(service: AuthService, session: AsyncMock, mock_user: MagicMock):
    token = create_refresh_token(mock_user.id)
    session.get.return_value = mock_user
    result = await service.refresh(token)
    assert "access_token" in result


@pytest.mark.asyncio
async def test_refresh_invalid_token(service: AuthService):
    with pytest.raises(InvalidTokenError):
        await service.refresh("token.invalido.xxx")


@pytest.mark.asyncio
async def test_refresh_wrong_type(service: AuthService):
    # Un access token no debe ser aceptado como refresh token
    token = create_access_token(uuid.uuid4(), "director")
    with pytest.raises(InvalidTokenError):
        await service.refresh(token)


@pytest.mark.asyncio
async def test_refresh_user_not_found(service: AuthService, mock_user: MagicMock, session: AsyncMock):
    # Token válido pero usuario eliminado — mismo error que token inválido (no revelar info)
    token = create_refresh_token(mock_user.id)
    session.get.return_value = None
    with pytest.raises(InvalidTokenError):
        await service.refresh(token)


# ── invite ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invite_success(service: AuthService, session: AsyncMock, mail: MagicMock):
    _mock_execute(session, None)
    await service.invite("nuevo@unq.edu.ar", "docente")
    mail.send.assert_called_once()


@pytest.mark.asyncio
async def test_invite_wrong_domain(service: AuthService):
    with pytest.raises(UnauthorizedDomainError):
        await service.invite("nuevo@gmail.com", "docente")


@pytest.mark.asyncio
async def test_invite_user_already_exists(service: AuthService, session: AsyncMock, mock_user: MagicMock):
    _mock_execute(session, mock_user)
    with pytest.raises(ConflictError):
        await service.invite("steve@unq.edu.ar", "docente")


# ── register ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_success(service: AuthService, session: AsyncMock):
    _mock_execute(session, None)  # no existe usuario activo con ese email
    token = create_invite_token("nuevo@unq.edu.ar", "docente")
    result = await service.register(token, "password123")
    assert "access_token" in result
    assert "refresh_token" in result


@pytest.mark.asyncio
async def test_register_invalid_token(service: AuthService):
    with pytest.raises(InvalidTokenError):
        await service.register("token.invalido.xxx", "password123")


@pytest.mark.asyncio
async def test_register_wrong_type(service: AuthService):
    # Un access token no debe funcionar como invite token
    token = create_access_token(uuid.uuid4(), "director")
    with pytest.raises(InvalidTokenError):
        await service.register(token, "password123")


@pytest.mark.asyncio
async def test_register_user_already_exists(service: AuthService, session: AsyncMock, mock_user: MagicMock):
    _mock_execute(session, mock_user)
    token = create_invite_token("steve@unq.edu.ar", "docente")
    with pytest.raises(ConflictError):
        await service.register(token, "password123")


# ── forgot_password ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_forgot_password_sends_email(
    service: AuthService, session: AsyncMock, mock_user: MagicMock, mail: MagicMock
):
    _mock_execute(session, mock_user)
    await service.forgot_password("steve@unq.edu.ar")
    mail.send.assert_called_once()


@pytest.mark.asyncio
async def test_forgot_password_silent_fail(service: AuthService, session: AsyncMock, mail: MagicMock):
    _mock_execute(session, None)
    await service.forgot_password("nadie@unq.edu.ar")
    mail.send.assert_not_called()


# ── reset_password ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reset_password_success(service: AuthService, session: AsyncMock, mock_user: MagicMock):
    token = create_reset_token(mock_user.id, mock_user.email)
    session.get.return_value = mock_user
    await service.reset_password(token, "nueva_pass123")
    session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password_invalid_token(service: AuthService):
    with pytest.raises(InvalidTokenError):
        await service.reset_password("token.invalido.xxx", "nueva_pass")


@pytest.mark.asyncio
async def test_reset_password_wrong_type(service: AuthService):
    # Un refresh token no debe funcionar como reset token
    token = create_refresh_token(uuid.uuid4())
    with pytest.raises(InvalidTokenError):
        await service.reset_password(token, "nueva_pass")


@pytest.mark.asyncio
async def test_reset_password_user_not_found(service: AuthService, mock_user: MagicMock, session: AsyncMock):
    # Token válido pero usuario eliminado — mismo error que token inválido (no revelar info)
    token = create_reset_token(mock_user.id, mock_user.email)
    session.get.return_value = None
    with pytest.raises(InvalidTokenError):
        await service.reset_password(token, "nueva_pass")
