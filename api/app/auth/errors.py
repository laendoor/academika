from app.errors import UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Credenciales inválidas")


class InvalidTokenError(UnauthorizedError):
    def __init__(self) -> None:
        super().__init__("Token inválido o expirado")


class UnauthorizedDomainError(UnauthorizedError):
    def __init__(self, domain: str) -> None:
        super().__init__(f"El email debe pertenecer al dominio {domain}")
