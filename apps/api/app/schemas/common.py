import uuid

from pydantic import BaseModel


class PaginatedResponse[T](BaseModel):
    total: int
    items: list[T]


class SearchHitResponse(BaseModel):
    """Coincidencia de autocompletado. `term` es lo que el usuario escribe en el filtro."""

    id: uuid.UUID
    label: str
    term: str
