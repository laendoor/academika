from app.models.materia import Materia
from app.schemas.materias import MateriaCreate, MateriaUpdate
from app.services.base import BaseService


class MateriaService(BaseService[Materia, MateriaCreate, MateriaUpdate]):
    model = Materia
