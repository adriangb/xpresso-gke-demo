from typing import Any, Mapping, Optional
from uuid import UUID

import asyncpg  # type: ignore[import]
from app.db.connection import InjectDBConnectionPool
from app.models.domain.users import User

Record = Mapping[str, Any]


class UserInDB(User):
    id: UUID
    hashed_password: str


GET_USER_BY_EMAIL = """\
SELECT id,
       username,
       email,
       hashed_password,
       bio,
       image,
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
       image,
FROM users
WHERE username = $1
LIMIT 1;
"""


CREATE_USER = """\
INSERT INTO users (username, email, hashed_password)
VALUES ($1, $2, $3)
"""

UPDATE_USER = """\
UPDATE
    users
WHERE id = $1
SET username        = $2,
    email           = COALESCE(email, $3),
    hashed_password = COALESCE(hashed_password, $4),
    bio             = COALESCE(bio, $5),
    image           = COALESCE(image, $6)
"""


class UsersRepository:
    def __init__(self, pool: InjectDBConnectionPool) -> None:
        self.pool = pool

    async def get_user_by_email(self, *, email: str) -> UserInDB | None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            user_row: Record | None = await conn.fetchrow(GET_USER_BY_EMAIL, email)
        if user_row:
            return UserInDB(**user_row)
        return None

    async def get_user_by_username(self, *, username: str) -> UserInDB | None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            user_row: Record | None = await conn.fetchrow(GET_USER_BY_NAME, username)
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
        async with self.pool.acquire() as conn:
            await conn.execute(
                CREATE_USER,
                username,
                email,
                hashed_password,
            )

    async def update_user(  # noqa: WPS211
        self,
        *,
        user_id: UUID,  # from JWT
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        bio: Optional[str] = None,
        image: Optional[str] = None,
    ) -> UserInDB:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            await conn.execute(
                UPDATE_USER,
                user_id,
                username,
                email,
                password,
                bio,
                image,
            )
