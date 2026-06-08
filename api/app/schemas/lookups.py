from pydantic import BaseModel


class EstadoAcademicoResponse(BaseModel):
    key: str
    label: str

    model_config = {"from_attributes": True}


class EstadoCursadaResponse(BaseModel):
    key: str
    code: str
    label: str

    model_config = {"from_attributes": True}


class TipoCursadaResponse(BaseModel):
    key: str
    label: str

    model_config = {"from_attributes": True}
