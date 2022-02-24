from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool
from app.db.repositories.exceptions import ResourceDoesNotExistError
from app.models.domain.profiles import Profile

Record = Mapping[str, Any]


QUERY_DIR = Path(__file__).parent / "sql" / "profiles"
GET_PROFILE = open(QUERY_DIR / "get_profile.sql").read()
FOLLOW_PROFILE = open(QUERY_DIR / "follow.sql").read()
UNFOLLOW_PROFILE = open(QUERY_DIR / "unfollow.sql").read()


@dataclass(slots=True)
class ProfilesRepo(Singleton):
    pool: InjectDBConnectionPool

    async def get_profile(
        self,
        *,
        current_user_id: UUID | None,
        username_of_target_profile: str,
    ) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            profile_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                GET_PROFILE,
                current_user_id,
                username_of_target_profile,
            )
            if profile_record is None:
                raise ResourceDoesNotExistError
            return Profile(**profile_record)

    async def follow_user(
        self,
        *,
        current_user_id: UUID,
        username_to_follow: str,
    ) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                profile_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                    FOLLOW_PROFILE, current_user_id, username_to_follow
                )
            except asyncpg.NotNullViolationError:
                raise ResourceDoesNotExistError
            return Profile(**profile_record, following=True)

    async def unfollow_user(
        self,
        *,
        current_user_id: UUID,
        username_to_unfollow: str,
    ) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            profile_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                UNFOLLOW_PROFILE, current_user_id, username_to_unfollow
            )
            if profile_record is None:
                raise ResourceDoesNotExistError
            return Profile(**profile_record, following=False)
