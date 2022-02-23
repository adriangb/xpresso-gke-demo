from dataclasses import dataclass
from typing import Annotated, Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
from xpresso import Depends

from app.db.connection import InjectDBConnectionPool

Record = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class UserInDB:
    id: UUID
    username: str
    email: str
    hashed_password: str
    bio: str | None
    image: str | None


GET_USER_BY_EMAIL = """\
SELECT id,
       username,
       email,
       hashed_password,
       bio,
       image
FROM users
WHERE email = $1
LIMIT 1;
"""


GET_USER_BY_NAME = """\
SELECT id,
       username,
       email,
       hashed_password,
       bio,
       image
FROM users
WHERE username = $1
LIMIT 1;
"""


GET_USER_BY_ID = """\
SELECT id,
       username,
       email,
       hashed_password,
       bio,
       image
FROM users
WHERE id = $1
LIMIT 1;
"""


CREATE_USER = """\
INSERT INTO users (username, email, hashed_password)
VALUES ($1, $2, $3)
RETURNING id
"""

UPDATE_USER = """\
UPDATE users
SET username        = COALESCE($2, username),
    email           = COALESCE($3, email),
    hashed_password = COALESCE($4, hashed_password),
    bio             = COALESCE($5, bio),
    image           = COALESCE($6, image)
WHERE id = $1
"""

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
class UsersRepository:
    pool: InjectDBConnectionPool

    async def get_user_by_email(self, email: str) -> UserInDB | None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            user_row: Record | None = await conn.fetchrow(GET_USER_BY_EMAIL, email)  # type: ignore  # for Pylance
        if user_row:
            return UserInDB(**user_row)
        return None

    async def get_user_by_username(self, username: str) -> UserInDB | None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            user_row: Record | None = await conn.fetchrow(GET_USER_BY_NAME, username)  # type: ignore  # for Pylance
        if user_row:
            return UserInDB(**user_row)
        return None

    async def get_user_by_id(self, id: UUID) -> UserInDB | None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            user_row: Record | None = await conn.fetchrow(GET_USER_BY_ID, id)  # type: ignore  # for Pylance
        if user_row:
            return UserInDB(**user_row)
        return None

    async def create_user(
        self,
        *,
        username: str,
        email: str,
        hashed_password: str,
    ) -> UUID:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            user_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                CREATE_USER,
                username,
                email,
                hashed_password,
            )
            return user_record["id"]  # type: ignore[no-any-return]

    async def update_user(
        self,
        *,
        id_of_current_user: UUID,  # from JWT
        username: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
        bio: str | None = None,
        image: str | None = None,
    ) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            await conn.execute(  # type: ignore  # for Pylance
                UPDATE_USER,
                id_of_current_user,
                username,
                email,
                hashed_password,
                bio,
                image,
            )

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


InjectUsersRepo = Annotated[UsersRepository, Depends(scope="app")]
