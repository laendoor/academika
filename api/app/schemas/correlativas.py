import uuid

from pydantic import BaseModel


class CorrelativaMateriaRef(BaseModel):
    id: uuid.UUID
    codigo: str
    nombre: str

    model_config = {"from_attributes": True}


class CorrelativaResponse(BaseModel):
    materia: CorrelativaMateriaRef
    requisito: CorrelativaMateriaRef
    es_obligatoria: bool

    model_config = {"from_attributes": True}
