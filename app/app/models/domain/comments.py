from pydantic import BaseModel

from app.models.common import DateTimeModelMixin
from app.models.domain.profiles import Profile


class Comment(DateTimeModelMixin, BaseModel):
    body: str
    author: Profile
