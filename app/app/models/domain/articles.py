from typing import List

from app.models.common import DateTimeModelMixin
from app.models.domain.profiles import Profile


class Article(DateTimeModelMixin):
    slug: str
    title: str
    description: str
    body: str
    tags: List[str]
    author: Profile
    favorited: bool
    favorites_count: int
