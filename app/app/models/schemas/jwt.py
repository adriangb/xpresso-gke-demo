from typing import Annotated, NewType

from pydantic import BaseModel, Field


class JWTUser(BaseModel):
    user_id: Annotated[str, Field(alias="sub")]
    exp: float


Token = NewType("Token", str)
