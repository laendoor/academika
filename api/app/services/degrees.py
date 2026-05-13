from app.models.degree import Degree
from app.schemas.degrees import DegreeCreate, DegreeUpdate
from app.services.base import BaseService


class DegreeService(BaseService[Degree, DegreeCreate, DegreeUpdate]):
    model = Degree
