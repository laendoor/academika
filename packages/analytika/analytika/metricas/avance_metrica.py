from collections import defaultdict
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from analytika.base import MetricaBase, MetricaResult
from analytika.errors import MetricaNotFoundError, MetricaParamError
from analytika.reglas import APROBADAS, clasificar_nota
from analytika.services import AlumnoService, CursadaService, PlanDeEstudioService
from analytika.utils.numeros import porcentaje
from analytika.utils.params import param, require_param

_GROUP_BY = {"area", "nucleo"}


def _group_by(params: dict[str, Any]) -> list[str]:
    value = param(params, "group_by")
    if value is None:
        return []
    fields = [field.strip().lower() for field in value.split(",") if field.strip()]
    unknown = set(fields) - _GROUP_BY
    if unknown:
        raise MetricaParamError(f"group_by desconocido: {', '.join(sorted(unknown))} (usá area o nucleo)")
    return list(dict.fromkeys(fields))


class AvanceMetrica(MetricaBase):
    """Porcentaje de avance por par (alumno, carrera), con cortes a pedido."""

    key = "avance"
    name = "Avance de carrera"

    async def run(self, session: AsyncSession, params: dict[str, Any]) -> MetricaResult:
        dni = require_param(params, "alu")
        alumno_service = AlumnoService(session)
        alumno = await alumno_service.find_by_dni(dni)
        if alumno is None:
            raise MetricaNotFoundError(f"alumno no encontrado: {dni}")
        group_by = _group_by(params)

        cursada_service = CursadaService(session)
        plan_service = PlanDeEstudioService(session)

        result: list[dict[str, Any]] = []
        for plan, plan_carrera in await alumno_service.pares(alumno.id, param(params, "carrera")):
            materias = await plan_service.materias(plan.id)
            plan_ids = {materia.id for materia in materias}
            cursadas = await cursada_service.notas_de_carrera(alumno.id, plan.carrera_id)
            aprobadas = {
                materia_id
                for materia_id, nota in cursadas
                if materia_id in plan_ids and clasificar_nota(nota) in APROBADAS
            }

            result.append(
                {
                    "carrera": plan_carrera.codigo,
                    "corte": "total",
                    "aprobadas": len(aprobadas),
                    "total": len(materias),
                    "porcentaje": porcentaje(len(aprobadas), len(materias)),
                }
            )
            for field in group_by:
                buckets: dict[str, list[int]] = defaultdict(lambda: [0, 0])
                for materia in materias:
                    key = getattr(materia, field) or f"sin {field}"
                    buckets[key][1] += 1
                    if materia.id in aprobadas:
                        buckets[key][0] += 1
                result += [
                    {
                        "carrera": plan_carrera.codigo,
                        "corte": f"{field}: {key}",
                        "aprobadas": aprobadas_del_corte,
                        "total": total_del_corte,
                        "porcentaje": porcentaje(aprobadas_del_corte, total_del_corte),
                    }
                    for key, (aprobadas_del_corte, total_del_corte) in sorted(buckets.items())
                ]
        return result
