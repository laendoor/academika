from typing import Any

from pydantic import BaseModel


class SettingResponse(BaseModel):
    key: str
    value: Any
    description: str | None

    model_config = {"from_attributes": True}


class SettingUpdate(BaseModel):
    value: Any
