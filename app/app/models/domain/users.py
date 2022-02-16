from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    bio: Optional[str] = None
    image: Optional[str] = None
