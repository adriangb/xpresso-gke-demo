from app.models.domain.profiles import Profile
from pydantic import BaseModel


class ProfileInResponse(BaseModel):
    profile: Profile
