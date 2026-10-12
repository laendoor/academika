from app.errors import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Credenciales incorrectas")


class InvalidTokenError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Token inválido o expirado")


class UnauthorizedDomainError(UnauthorizedError):
    def __init__(self, allowed: list[str]) -> None:
        if len(allowed) == 1:
            super().__init__(f"El email debe pertenecer al dominio {allowed[0]}")
        else:
            super().__init__(f"El email debe pertenecer a uno de los dominios: {', '.join(allowed)}")
