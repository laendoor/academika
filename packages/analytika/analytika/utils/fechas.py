from datetime import date

from analytika.errors import MetricaParamError
from analytika.reglas import periodo_cuatrimestral


def parse_year(value: str, key: str) -> int:
    if not value.isdigit():
        raise MetricaParamError(f"'{key}' debe ser un número: {value}")
    return int(value)


def periodo(anio: int, cuatrimestre: str, fecha: date | None) -> str:
    """Período de una cursada: la fecha manda; sin fecha, el cuatrimestre guardado."""
    if fecha is not None:
        return periodo_cuatrimestral(fecha)
    return f"{anio}-S1" if cuatrimestre.startswith("1") else f"{anio}-S2"


def indice_periodo(periodo: str) -> int:
    """Índice lineal de un período 'YYYY-Sn' para comparar y restar cuatrimestres."""
    anio, semestre = periodo.split("-S")
    return int(anio) * 2 + int(semestre) - 1
