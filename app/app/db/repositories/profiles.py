from dataclasses import dataclass
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
import asyncpg.exceptions  # type: ignore[import]

from app.db.connection import InjectDBConnectionPool

Record = Mapping[str, Any]


FOLLOW_USER_AND_RETURN_THEIR_PROFILE = """\
WITH followed_profile AS (
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
        (SELECT id from followed_profile)
    )
)
SELECT username, bio, image FROM followed_profile;
"""

UNFOLLOW_USER_AND_RETURN_THEIR_PROFILE = """\
WITH followed_profile AS (
    SELECT id, username, bio, image
    FROM users
    WHERE username = $1
), _ AS (
    DELETE FROM followers_to_followings
    -- $2 is the follower id, which we get from the user's token
    WHERE (follower_id = $2 and following_id = (SELECT id from followed_profile))
)
SELECT username, bio, image FROM followed_profile;
"""


CHECK_IF_FOLLOWING_AND_RETURN_PROFILE = """\
WITH followed_profile AS (
        SELECT id, username, bio, image
        FROM users
        WHERE username = $1
    ),
    follows AS (
        SELECT exists(
            SELECT 1 FROM followers_to_followings
            -- $2 is the follower id, which we get from the user's token
            WHERE (follower_id = $2 and following_id = (SELECT id from followed_profile))
        ) AS follows
    )
SELECT username, bio, image, follows FROM followed_profile CROSS JOIN follows;
"""


@dataclass(frozen=True, slots=True)
class Profile:
    username: str
    image: str | None
    bio: str | None
    follows: bool


class FolloweeDoesNotExist(Exception):
    pass


@dataclass(frozen=True, slots=True, eq=False)
class ProfilesRepository:
    pool: InjectDBConnectionPool

    async def follow_user(
        self, username_to_follow: str, id_of_current_user: UUID
    ) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                followed_profile: Record = await conn.fetchrow(FOLLOW_USER_AND_RETURN_THEIR_PROFILE, username_to_follow, id_of_current_user)  # type: ignore  # for Pylance
            except asyncpg.exceptions.NotNullViolationError as e:
                # the user `username_to_follow` does not exist in the DB
                raise FolloweeDoesNotExist from e
            return Profile(**followed_profile, follows=True)

    async def unfollow_user(
        self, username_to_unfollow: str, id_of_current_user: UUID
    ) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                unfollowed_profile: Record = await conn.fetchrow(UNFOLLOW_USER_AND_RETURN_THEIR_PROFILE, username_to_unfollow, id_of_current_user)  # type: ignore  # for Pylance
            except asyncpg.exceptions.NotNullViolationError as e:
                # the user `username_to_unfollow` does not exist in the DB
                raise FolloweeDoesNotExist from e
            return Profile(**unfollowed_profile, follows=False)

    async def get_profile(
        self, username_of_target_profile: str, id_of_current_user: UUID | None
    ) -> Profile:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                unfollowed_profile: Record = await conn.fetchrow(CHECK_IF_FOLLOWING_AND_RETURN_PROFILE, username_of_target_profile, id_of_current_user)  # type: ignore  # for Pylance
            except asyncpg.exceptions.NotNullViolationError as e:
                # the user `username_to_unfollow` does not exist in the DB
                raise FolloweeDoesNotExist from e
            return Profile(**unfollowed_profile)
