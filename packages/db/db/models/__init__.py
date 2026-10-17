from db.models.alumno import Alumno
from db.models.alumno_carrera import AlumnoCarrera
from db.models.carrera import Carrera
from db.models.correlativa import Correlativa
from db.models.cursada import Cursada
from db.models.lkp_estado_academico import LkpEstadoAcademico
from db.models.lkp_estado_cursada import LkpEstadoCursada
from db.models.lkp_log_action import LkpLogAction
from db.models.lkp_log_status import LkpLogStatus
from db.models.lkp_nivel_carrera import LkpNivelCarrera
from db.models.lkp_nucleo_carrera import LkpNucleoCarrera
from db.models.lkp_tipo_cursada import LkpTipoCursada
from db.models.lkp_user_role import LkpUserRole
from db.models.log_event import LogEvent
from db.models.materia import Materia
from db.models.plan_de_estudio import PlanDeEstudio
from db.models.planes_materias import planes_materias
from db.models.setting import Setting
from db.models.user import User

__all__ = [
    "Alumno",
    "AlumnoCarrera",
    "Carrera",
    "Correlativa",
    "Cursada",
    "LogEvent",
    "LkpEstadoAcademico",
    "LkpEstadoCursada",
    "LkpLogAction",
    "LkpLogStatus",
    "LkpNivelCarrera",
    "LkpNucleoCarrera",
    "LkpTipoCursada",
    "LkpUserRole",
    "Materia",
    "PlanDeEstudio",
    "Setting",
    "User",
    "planes_materias",
]
