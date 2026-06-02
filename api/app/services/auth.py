import uuid

import resend
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.assertions import ensure_authorized_domain, ensure_token_decoded
from app.auth.errors import InvalidCredentialsError, InvalidTokenError
from app.auth.password import hash_password, verify_password
from app.auth.tokens import create_access_token, create_refresh_token, create_reset_token
from app.config import settings
from app.db.session import SessionDep
from app.models.user import User


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def dep(cls, session: SessionDep) -> "AuthService":
        return cls(session)

    async def login(self, email: str, password: str) -> dict:
        ensure_authorized_domain(email)

        result = await self.session.execute(select(User).where(User.email == email, User.is_active))
        user = result.scalar_one_or_none()

        if user and verify_password(password, user.hashed_password):
            return {
                "access_token": create_access_token(user.id, user.role),
                "refresh_token": create_refresh_token(user.id),
            }

        raise InvalidCredentialsError()

    async def refresh(self, refresh_token: str) -> dict:
        payload = ensure_token_decoded(refresh_token, "refresh")

        user = await self.session.get(User, uuid.UUID(payload["sub"]))
        if user and user.is_active:
            return {"access_token": create_access_token(user.id, user.role)}

        raise InvalidTokenError()

    async def forgot_password(self, email: str) -> None:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            return  # silent fail — no revelar si el email existe

        token = create_reset_token(user.id, user.email)
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"

        resend.api_key = settings.resend_api_key
        resend.Emails.send(
            {
                "from": settings.resend_from_email,
                "to": user.email,
                "subject": "Recuperación de contraseña — Académika",
                "html": (
                    f'<p>Hacé clic <a href="{reset_url}">acá</a> para resetear tu contraseña.'
                    " El enlace expira en 1 hora.</p>"
                ),
            }
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        payload = ensure_token_decoded(token, "reset")

        user = await self.session.get(User, uuid.UUID(payload["sub"]))
        if user is None:
            raise InvalidTokenError()

        user.hashed_password = hash_password(new_password)
        await self.session.commit()
