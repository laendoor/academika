import logging
from datetime import date

PROMOCIONADO = "promocionado"
APROBADO = "aprobado"
EQUIVALENCIA = "equivalencia"
DESAPROBADO = "desaprobado"
PENDIENTE_APROBACION = "pendiente_aprobacion"

APROBADAS = frozenset({PROMOCIONADO, APROBADO, EQUIVALENCIA})

_NOTA_MIN_APROBADO = 4
_NOTA_MIN_PROMOCIONADO = 6

logger = logging.getLogger(__name__)


def clasificar_nota(nota: str | None) -> str:
    """Clasifica una cursada por su nota (D4 de #96).

    Los códigos no numéricos del export (`A`, `D`, `PA`) y la ausencia de nota
    se resuelven acá para que las métricas compartan un solo criterio.
    """
    if nota is None or not nota.strip():
        return PENDIENTE_APROBACION

    value = nota.strip().upper()
    if value == "A":
        return EQUIVALENCIA
    if value == "D":
        return DESAPROBADO
    if value == "PA":
        return PENDIENTE_APROBACION
    if not value.isdigit():
        logger.error("nota desconocida '%s' — se clasifica como pendiente", nota)
        return PENDIENTE_APROBACION

    numero = int(value)
    if numero >= _NOTA_MIN_PROMOCIONADO:
        return PROMOCIONADO
    if numero >= _NOTA_MIN_APROBADO:
        return APROBADO
    return DESAPROBADO


def periodo_cuatrimestral(fecha: date) -> str:
    """S1 = jun-oct; S2 = nov-may, etiquetado con el año de inicio (D5 de #96).

    Entre 2023 y 2026 el calendario de la UNQ repite la misma estructura: las
    mesas de S1 caen en jul (libres), sep (integradores) y oct (libres e
    integradores); las de S2, en dic, feb y may del año siguiente. Junio y
    noviembre no tienen mesas y pertenecen a la cursada en curso.
    """
    if 6 <= fecha.month <= 10:
        return f"{fecha.year}-S1"
    if fecha.month >= 11:
        return f"{fecha.year}-S2"
    return f"{fecha.year - 1}-S2"
