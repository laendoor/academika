from typing import Literal

from pydantic import BaseModel, Field

UserRole = Literal["admin", "director", "docente"]


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(AuthTokens): ...


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class InviteRequest(BaseModel):
    email: str
    role: UserRole


class RegisterRequest(BaseModel):
    token: str
    password: str = Field(min_length=8)


class RegisterResponse(AuthTokens): ...


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
