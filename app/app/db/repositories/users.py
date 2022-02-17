from dataclasses import dataclass
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]

from app.db.connection import InjectDBConnectionPool

Record = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class UserInDB:
    id: UUID
    username: str
    email: str
    hashed_password: str
    bio: str | None = None
    image: str | None = None


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
"""

UPDATE_USER = """\
UPDATE users
SET username        = COALESCE(username, $2),
    email           = COALESCE(email, $3),
    hashed_password = COALESCE(hashed_password, $4),
    bio             = COALESCE(bio, $5),
    image           = COALESCE(image, $6)
WHERE id = $1
"""


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
    ) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            await conn.execute(  # type: ignore  # for Pylance
                CREATE_USER,
                username,
                email,
                hashed_password,
            )

    async def update_user(
        self,
        *,
        user_id: UUID,  # from JWT
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
                user_id,
                username,
                email,
                hashed_password,
                bio,
                image,
            )
