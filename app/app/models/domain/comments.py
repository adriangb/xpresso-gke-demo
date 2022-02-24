from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.models.domain.profiles import Profile


@dataclass(slots=True)
class Comment:
    id: UUID
    created_at: datetime
    updated_at: datetime
    body: str
    author: Profile
