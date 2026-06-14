import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.assertions import ensure_authorized_domain, ensure_token_decoded
from app.auth.errors import InvalidCredentialsError, InvalidTokenError
from app.auth.password import hash_password, verify_password
from app.auth.tokens import create_access_token, create_invite_token, create_refresh_token, create_reset_token
from app.config import settings
from app.db.session import SessionDep
from app.errors import ConflictError
from app.schemas.users import UserCreate
from app.services.mail import MailService, get_mail_service
from app.services.users import UserService


class AuthService:
    def __init__(self, session: AsyncSession, users: UserService, mail: MailService) -> None:
        self.session = session
        self.users = users
        self.mail = mail

    @classmethod
    def dep(
        cls,
        session: SessionDep,
        users: Annotated[UserService, Depends(UserService.dep)],
        mail: Annotated[MailService, Depends(get_mail_service)],
    ) -> "AuthService":
        return cls(session, users, mail)

    async def login(self, email: str, password: str) -> dict:
        ensure_authorized_domain(email)

        user = await self.users.find_active_by_email(email)

        if user and verify_password(password, user.hashed_password):
            return {
                "access_token": create_access_token(user.id, user.role),
                "refresh_token": create_refresh_token(user.id),
            }

        raise InvalidCredentialsError()

    async def refresh(self, refresh_token: str) -> dict:
        payload = ensure_token_decoded(refresh_token, "refresh")

        user = await self.users.find_by_id(uuid.UUID(payload["sub"]))
        if user and user.is_active:
            return {"access_token": create_access_token(user.id, user.role)}

        raise InvalidTokenError()

    async def invite(self, email: str, role: str) -> None:
        ensure_authorized_domain(email)

        if await self.users.find_active_by_email(email) is not None:
            raise ConflictError(f"Ya existe un usuario activo con email '{email}'")

        token = create_invite_token(email, role)
        invite_url = f"{settings.frontend_url}/register?token={token}"

        self.mail.send(
            to=email,
            subject="Invitación a Académika",
            html=(
                f'<p>Fuiste invitado a Académika. <a href="{invite_url}">Completá tu registro acá</a>.'
                f" El enlace expira en {settings.invite_token_expire_hours} horas.</p>"
            ),
        )

    async def register(self, token: str, password: str) -> dict:
        payload = ensure_token_decoded(token, "invite")
        email = payload["sub"]
        role = payload["role"]

        if await self.users.find_active_by_email(email) is not None:
            raise ConflictError(f"Ya existe un usuario activo con email '{email}'")

        user = await self.users.create(UserCreate(email=email, role=role, hashed_password=hash_password(password)))
        return {
            "access_token": create_access_token(user.id, user.role),
            "refresh_token": create_refresh_token(user.id),
        }

    async def forgot_password(self, email: str) -> None:
        user = await self.users.find_by_email(email)
        if user is None:
            return  # silent fail — no revelar si el email existe

        token = create_reset_token(user.id, user.email)
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"

        self.mail.send(
            to=user.email,
            subject="Recuperación de contraseña - Academika",
            html=(
                f'<p>Hacé clic <a href="{reset_url}">acá</a> para resetear tu contraseña.'
                " El enlace expira en 1 hora.</p>"
            ),
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        payload = ensure_token_decoded(token, "reset")

        user = await self.users.find_by_id(uuid.UUID(payload["sub"]))
        if user is None:
            raise InvalidTokenError()

        user.hashed_password = hash_password(new_password)
        await self.session.commit()
