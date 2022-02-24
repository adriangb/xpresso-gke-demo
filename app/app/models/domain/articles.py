from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.models.domain.profiles import Profile


@dataclass(slots=True)
class Article:
    id: UUID
    title: str
    description: str
    body: str
    author: Profile
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    favorited: bool
    favorites_count: int
