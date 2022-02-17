from pydantic import BaseModel

from app.models.schemas.configs import ModelInResponseConfig


class Profile(BaseModel):
    username: str
    following: bool
    bio: str | None
    image: str | None


class ProfileInResponse(BaseModel):
    profile: Profile

    Config = ModelInResponseConfig
