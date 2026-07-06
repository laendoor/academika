from pydantic import BaseModel


class ImportResult(BaseModel):
    type: str
    files: list[str]
    processed: int
    skipped: int


class ImportFailure(BaseModel):
    file: str
    error: str


class ImportResponse(BaseModel):
    results: list[ImportResult]
    errors: list[ImportFailure]
