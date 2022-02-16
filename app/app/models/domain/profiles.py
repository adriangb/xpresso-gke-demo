from typing import Optional

from pydantic import BaseModel


class Profile(BaseModel):
    username: str
    following: bool
    bio: Optional[str]
    image: Optional[str]
