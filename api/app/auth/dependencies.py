import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.assertions import ensure_token_decoded
from app.auth.errors import InvalidTokenError
from app.db.session import SessionDep
from app.errors import ForbiddenError
from app.models.user import User

_bearer = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    session: SessionDep,
) -> User:
    payload = ensure_token_decoded(credentials.credentials, expected_type="access")
    user = await session.get(User, uuid.UUID(payload["sub"]))
    if user and user.is_active:
        return user
    raise InvalidTokenError()


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: str):
    async def dependency(user: CurrentUser) -> User:
        if user.role not in roles:
            raise ForbiddenError()
        return user

    return dependency
