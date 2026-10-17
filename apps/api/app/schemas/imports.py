from typing import Literal

from pydantic import BaseModel


class ImportAcceptedResponse(BaseModel):
    status: Literal["processing"]
    count: int
