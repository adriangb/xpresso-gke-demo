from datetime import datetime
from typing import Annotated, NewType
from uuid import UUID

from pydantic import BaseModel, Field


class JWTUser(BaseModel):
    user_id: Annotated[UUID, Field(alias="sub")]
    exp: datetime


Token = NewType("Token", str)
