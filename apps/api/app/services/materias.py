from db.models.materia import Materia
from db.search import search_criteria
from sqlalchemy import select

from app.schemas.materias import MateriaCreate, MateriaUpdate
from app.services.base import BaseService


class MateriaService(BaseService[Materia, MateriaCreate, MateriaUpdate]):
    model = Materia

    async def search(self, q: str, limit: int = 8) -> list[Materia]:
        criteria = search_criteria(Materia.search_term, q)
        if not criteria:
            return []
        stmt = select(Materia).where(*criteria).order_by(Materia.nombre).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())
