from typing import Any


class AcademikaError(Exception):
    @property
    def detail(self) -> str:
        return str(self)


class NotFoundError(AcademikaError):
    def __init__(self, resource: str, id: Any) -> None:
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} '{id}' no encontrado")


class ConflictError(AcademikaError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class BusinessError(AcademikaError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)
