from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    bio: str | None = None
    image: str | None = None
