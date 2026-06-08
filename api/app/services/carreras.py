from app.models.carrera import Carrera
from app.schemas.carreras import CarreraCreate, CarreraUpdate
from app.services.base import BaseService


class CarreraService(BaseService[Carrera, CarreraCreate, CarreraUpdate]):
    model = Carrera
