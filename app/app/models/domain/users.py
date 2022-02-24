from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class User:
    id: UUID
    username: str
    email: str
    bio: str | None
    image: str | None
    hashed_password: str
