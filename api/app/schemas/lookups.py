from pydantic import BaseModel


class AcademicStatusResponse(BaseModel):
    key: str
    label: str

    model_config = {"from_attributes": True}


class EnrollmentStatusResponse(BaseModel):
    key: str
    code: str
    label: str

    model_config = {"from_attributes": True}


class EnrollmentTypeResponse(BaseModel):
    key: str
    label: str

    model_config = {"from_attributes": True}
