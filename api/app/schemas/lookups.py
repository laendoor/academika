from pydantic import BaseModel


class LookupResponse(BaseModel):
    key: str
    label: str

    model_config = {"from_attributes": True}


class EstadoAcademicoResponse(LookupResponse): ...


class EstadoCursadaResponse(LookupResponse):
    code: str


class TipoCursadaResponse(LookupResponse): ...


class UserRoleResponse(LookupResponse): ...
