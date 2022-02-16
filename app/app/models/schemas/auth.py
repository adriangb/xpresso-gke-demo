from pydantic import BaseModel


class Unauthorized(BaseModel):
    reason: str


class Forbidden(BaseModel):
    reason: str
