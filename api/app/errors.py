from typing import Any


class AcademikaError(Exception):
    status_code: int = 500

    @property
    def detail(self) -> str:
        return str(self)


class NotFoundError(AcademikaError):
    status_code = 404

    def __init__(self, resource: str, id: Any) -> None:
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} '{id}' no encontrado")


class ConflictError(AcademikaError):
    status_code = 409

    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class BusinessError(AcademikaError):
    status_code = 422

    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class UnauthorizedError(AcademikaError):
    status_code = 401

    def __init__(self, detail: str = "No autorizado") -> None:
        super().__init__(detail)


class ForbiddenError(AcademikaError):
    status_code = 403

    def __init__(self, detail: str = "Acceso denegado") -> None:
        super().__init__(detail)


class DetectorError(BusinessError):
    """Raised when a planilla's type cannot be detected from its headers."""
