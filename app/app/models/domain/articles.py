from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.models.domain.profiles import Profile


class Article(BaseModel):
    slug: str
    title: str
    description: str
    body: str
    tags: List[str]
    author: Profile
    favorited: bool
    favorites_count: int
    created_at: datetime
    updated_at: datetime
