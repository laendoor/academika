from collections import defaultdict
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from analytika.base import MetricaBase, MetricaResult
from analytika.services import AlumnoService, CursadaService
from analytika.utils.fechas import indice_periodo, periodo
from analytika.utils.numeros import nota_numerica, promedio
from analytika.utils.params import param


class PromediosMetrica(MetricaBase):
    """Promedios de la cohorte: general, sin aplazos y ventana reciente por alumno."""

    key = "promedios"
    name = "Promedios"

    async def run(self, session: AsyncSession, params: dict[str, Any]) -> MetricaResult:
        pairs = AlumnoService.pares_cohorte_query(
            param(params, "carrera"), param(params, "ingreso"), param(params, "estado"), param(params, "plan")
        )
        rows = await CursadaService(session).notas_cohorte(pairs)

        # shortcut: la ventana reciente se computa en Python sobre las cursadas filtradas.
        # Con volumen alto, pasar a window function en SQL.
        by_alumno: dict[Any, list[tuple[str, int | None]]] = defaultdict(list)
        for alumno_id, anio, cuatrimestre, nota, fecha in rows:
            by_alumno[alumno_id].append((periodo(anio, cuatrimestre, fecha), nota_numerica(nota)))

        todas = [nota for registros in by_alumno.values() for _, nota in registros if nota is not None]
        recientes: list[int] = []
        for registros in by_alumno.values():
            ancla = max(indice_periodo(clave) for clave, _ in registros)
            recientes += [nota for clave, nota in registros if indice_periodo(clave) >= ancla - 2 and nota is not None]

        return [
            {
                "general": promedio(todas),
                "general_sin_aplazos": promedio([nota for nota in todas if nota >= 4]),
                "reciente": promedio(recientes),
                "reciente_sin_aplazos": promedio([nota for nota in recientes if nota >= 4]),
            }
        ]
