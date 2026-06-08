import uuid

from app.db.query_builder import QueryBuilder
from app.models.cursada import Cursada
from app.schemas.cursadas import CursadaCreate, CursadaUpdate
from app.services.base import BaseService


class CursadaService(BaseService[Cursada, CursadaCreate, CursadaUpdate]):
    model = Cursada

    async def list_filtered(
        self,
        skip: int = 0,
        limit: int = 20,
        alumno_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        anio: int | None = None,
        cuatrimestre: str | None = None,
    ) -> tuple[int, list[Cursada]]:
        builder = QueryBuilder(Cursada)
        if alumno_id is not None:
            builder.filter(Cursada.alumno_id == alumno_id)
        if materia_id is not None:
            builder.filter(Cursada.materia_id == materia_id)
        if anio is not None:
            builder.filter(Cursada.anio == anio)
        if cuatrimestre is not None:
            builder.filter(Cursada.cuatrimestre == cuatrimestre)
        total = await self.session.scalar(builder.count_stmt())
        result = await self.session.execute(builder.paginated(skip, limit))
        return total or 0, list(result.scalars().all())
