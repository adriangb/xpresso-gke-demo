from app.models.common import DateTimeModelMixin
from app.models.domain.profiles import Profile
from pydantic import BaseModel


class Comment(DateTimeModelMixin, BaseModel):
    body: str
    author: Profile
