from typing import Literal

from pydantic import BaseModel

SheetTypeLiteral = Literal[
    "carreras",
    "materias",
    "planes_de_estudio",
    "correlativas",
    "alumnos",
    "historial_cursadas",
    "inscripciones",
]


class ImportResult(BaseModel):
    type: SheetTypeLiteral
    files: list[str]
    processed: int
    skipped: int


class ImportFailure(BaseModel):
    file: str
    error: str


class ImportResponse(BaseModel):
    results: list[ImportResult]
    errors: list[ImportFailure]
