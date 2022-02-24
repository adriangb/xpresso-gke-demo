from dataclasses import dataclass


@dataclass(slots=True)
class Profile:
    username: str
    bio: str | None
    image: str | None
    following: bool
