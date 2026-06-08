from app.models.alumno import Alumno
from app.models.alumno_carrera import AlumnoCarrera
from app.models.carrera import Carrera
from app.models.correlativa import Correlativa
from app.models.cursada import Cursada
from app.models.lkp_estado_academico import LkpEstadoAcademico
from app.models.lkp_estado_cursada import LkpEstadoCursada
from app.models.lkp_nivel_carrera import LkpNivelCarrera
from app.models.lkp_nucleo_carrera import LkpNucleoCarrera
from app.models.lkp_tipo_cursada import LkpTipoCursada
from app.models.lkp_user_role import LkpUserRole
from app.models.materia import Materia
from app.models.plan_de_estudio import PlanDeEstudio
from app.models.planes_materias import planes_materias
from app.models.user import User

__all__ = [
    "Alumno",
    "AlumnoCarrera",
    "Carrera",
    "Correlativa",
    "Cursada",
    "LkpEstadoAcademico",
    "LkpEstadoCursada",
    "LkpNivelCarrera",
    "LkpNucleoCarrera",
    "LkpTipoCursada",
    "LkpUserRole",
    "Materia",
    "PlanDeEstudio",
    "User",
    "planes_materias",
]
