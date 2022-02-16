from dataclasses import dataclass
from typing import Any, Mapping, Optional
from uuid import UUID

import asyncpg  # type: ignore[import]
import asyncpg.exceptions  # type: ignore[import]

from app.db.connection import InjectDBConnectionPool

Record = Mapping[str, Any]


FOLLOW_USER_AND_GET_THEIR_PROFILE = """\
WITH followed_user AS (
    SELECT id, username, bio, image
    FROM users
    WHERE username = $1
), _ AS (
    INSERT INTO followers_to_followings (follower_id, following_id)
    VALUES (
        -- This is the follower_id, we know their user id from the token
        ($2),
        -- But we don't know the id of the user they want to follow
        -- We pull it from the CTE
        (SELECT id from followed_user)
    )
)
SELECT username, bio, image FROM followed_user;
"""

UNFOLLOW_USER_AND_GET_THEIR_PROFILE = """\
WITH followed_user AS (
    SELECT id, username, bio, image
    FROM users
    WHERE username = $1
), _ AS (
    DELETE FROM followers_to_followings
    -- $2 is the follower id, which we get from the user's token
    WHERE (follower_id = $2 and following_id = (SELECT id from followed_user))
)
SELECT username, bio, image FROM followed_user;
"""


@dataclass(frozen=True, slots=True)
class Profile:
    username: str
    image: Optional[str]
    bio: Optional[str]


class FollowedUserDoesNotExist(Exception):
    pass


@dataclass(frozen=True, slots=True, eq=False)
class ProfilesRepository:
    pool: InjectDBConnectionPool

    async def follow_user(self, username_to_follow: str, user_id: UUID) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                followed_profile: Record = await conn.fetchrow(FOLLOW_USER_AND_GET_THEIR_PROFILE, username_to_follow, user_id)  # type: ignore  # for Pylance
            except asyncpg.exceptions.NotNullViolationError as e:
                # the user `username_to_follow` does not exist in the DB
                raise FollowedUserDoesNotExist from e
            return Profile(**followed_profile)

    async def unfollow_user(self, username_to_unfollow: str, user_id: UUID) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                unfollowed_profile: Record = await conn.fetchrow(UNFOLLOW_USER_AND_GET_THEIR_PROFILE, username_to_unfollow, user_id)  # type: ignore  # for Pylance
            except asyncpg.exceptions.NotNullViolationError as e:
                # the user `username_to_unfollow` does not exist in the DB
                raise FollowedUserDoesNotExist from e
            return Profile(**unfollowed_profile)
