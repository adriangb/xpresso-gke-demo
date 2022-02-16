from typing import Optional

from pydantic import BaseModel


class Profile(BaseModel):
    username: str
    bio: str = ""
    image: Optional[str] = None
    following: bool = False
