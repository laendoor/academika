from pydantic import BaseModel


class MetricaInfo(BaseModel):
    key: str
    name: str
