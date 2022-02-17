from pydantic import BaseModel


class Profile(BaseModel):
    username: str
    following: bool
    bio: str | None
    image: str | None
