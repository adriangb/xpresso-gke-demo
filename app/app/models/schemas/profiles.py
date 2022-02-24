from pydantic import BaseModel

from app.models.domain.profiles import Profile as ProfileDomainModel
from app.models.schemas.configs import ModelInResponseConfig


class Profile(BaseModel):
    username: str
    following: bool
    bio: str | None
    image: str | None

    @staticmethod
    def from_domain_model(profile: ProfileDomainModel) -> "Profile":
        return Profile.construct(
            username=profile.username,
            following=profile.following,
            bio=profile.bio,
            image=profile.image,
        )


class ProfileInResponse(BaseModel):
    profile: Profile

    Config = ModelInResponseConfig
