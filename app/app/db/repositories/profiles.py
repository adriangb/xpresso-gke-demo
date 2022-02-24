from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool
from app.models.domain.profiles import Profile


Record = Mapping[str, Any]


QUERY_DIR = Path(__file__).parent / "sql" / "profiles"
FOLLOW_PROFILE = open(QUERY_DIR / "follow.sql").read()
UNFOLLOW_PROFILE = open(QUERY_DIR / "unfollow.sql").read()


class FolloweeDoesNotExist(Exception):
    pass



@dataclass(slots=True)
class ProfilesRepo(Singleton):
    pool: InjectDBConnectionPool


    async def follow_user(
        self, username_to_follow: str, id_of_current_user: UUID
    ) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                followed_profile: Record = await conn.fetchrow(FOLLOW_PROFILE, id_of_current_user, username_to_follow)  # type: ignore  # for Pylance
            except asyncpg.exceptions.NotNullViolationError as e:
                # the user `username_to_follow` does not exist in the DB
                raise FolloweeDoesNotExist from e
            return Profile(**followed_profile, following=True)

    async def unfollow_user(
        self, username_to_unfollow: str, id_of_current_user: UUID
    ) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                unfollowed_profile: Record = await conn.fetchrow(UNFOLLOW_PROFILE, id_of_current_user, username_to_unfollow)  # type: ignore  # for Pylance
            except asyncpg.exceptions.NotNullViolationError as e:
                # the user `username_to_unfollow` does not exist in the DB
                raise FolloweeDoesNotExist from e
            return Profile(**unfollowed_profile, following=False)
