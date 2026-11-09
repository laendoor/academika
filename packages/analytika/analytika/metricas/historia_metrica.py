from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from analytika.base import MetricaBase, MetricaResult
from analytika.errors import MetricaNotFoundError
from analytika.reglas import clasificar_nota
from analytika.services import AlumnoService, CursadaService
from analytika.utils.params import param, require_param


class HistoriaMetrica(MetricaBase):
    """Historia académica de un alumno, una fila por cursada."""

    key = "historia"
    name = "Historia académica"

    async def run(self, session: AsyncSession, params: dict[str, Any]) -> MetricaResult:
        dni = require_param(params, "alu")
        alumno = await AlumnoService(session).find_by_dni(dni)
        if alumno is None:
            raise MetricaNotFoundError(f"alumno no encontrado: {dni}")

        rows = await CursadaService(session).historia(alumno.id, param(params, "carrera"))
        return [
            {
                "carrera": cursada_carrera.codigo,
                "cod_mat": materia.codigo,
                "materia": materia.nombre,
                "nota": cursada.nota,
                "estado": clasificar_nota(cursada.nota),
                "fecha": cursada.fecha_inscripcion.isoformat() if cursada.fecha_inscripcion else None,
            }
            for cursada, materia, cursada_carrera in rows
        ]
