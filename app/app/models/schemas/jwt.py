from datetime import datetime
from typing import Annotated, NewType
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.networks import EmailStr


class JWTUser(BaseModel):
    user_id: Annotated[UUID, Field(alias="sub")]
    exp: datetime
    email: Annotated[EmailStr, Field(alias="http://realworld.example.com/email")]


Token = NewType("Token", str)
