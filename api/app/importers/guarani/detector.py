from enum import StrEnum
from pathlib import Path

from app.errors import DetectorError
from app.utils.csv import read_headers
from app.utils.strings import is_integer


class GuaraniSheetType(StrEnum):
    CARRERAS = "carreras"
    MATERIAS = "materias"
    PLANES = "planes_de_estudio"
    CORRELATIVAS = "correlativas"
    ALUMNOS = "alumnos"
    HISTORIAL_CURSADAS = "historial_cursadas"
    INSCRIPCIONES = "inscripciones"


def detect_type(path: Path) -> GuaraniSheetType:
    headers = read_headers(path)
    if not headers:
        raise DetectorError("archivo vacío")
    cols = set(headers)

    if "obligatorias" in cols:
        return GuaraniSheetType.CORRELATIVAS
    if "comisión" in cols:
        return GuaraniSheetType.INSCRIPCIONES
    if "regular" in cols or "result" in cols:
        return GuaraniSheetType.HISTORIAL_CURSADAS
    if "nucleo" in cols or "cuatrimestre" in cols:
        return GuaraniSheetType.PLANES
    if "apellido" in cols and "email" in cols:
        return GuaraniSheetType.ALUMNOS
    if cols <= {"codigo", "nombre", "fecha"} and "codigo" in cols and "nombre" in cols:
        return GuaraniSheetType.CARRERAS
    if len(headers) == 5 and is_integer(headers[1]):
        return GuaraniSheetType.MATERIAS

    raise DetectorError(f"no se pudo detectar el tipo de planilla: headers={headers}")
