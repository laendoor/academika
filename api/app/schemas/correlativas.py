import uuid

from pydantic import BaseModel


class MateriaRef(BaseModel):
    id: uuid.UUID
    codigo: str
    nombre: str

    model_config = {"from_attributes": True}


class CorrelativaResponse(BaseModel):
    materia: MateriaRef
    requisito: MateriaRef
    es_obligatoria: bool

    model_config = {"from_attributes": True}
