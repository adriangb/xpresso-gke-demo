from typing import Annotated, Optional
from uuid import UUID

from app.models.common import DateTimeModelMixin
from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    bio: Optional[str] = None
    image: Optional[str] = None
