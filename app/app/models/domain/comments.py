from datetime import datetime

from pydantic import BaseModel

from app.models.domain.profiles import Profile


class Comment(BaseModel):
    body: str
    author: Profile
    created_at: datetime
    updated_at: datetime
