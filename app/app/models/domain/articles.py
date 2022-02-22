from datetime import datetime

from pydantic import BaseModel

from app.models.domain.profiles import Profile


class Article(BaseModel):
    slug: str
    title: str
    description: str
    body: str
    tags: list[str]
    author: Profile
    favorited: bool
    favorites_count: int
    created_at: datetime
    updated_at: datetime
