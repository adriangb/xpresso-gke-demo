from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool
from app.db.repositories.exceptions import (
    ResourceAlreadyExists,
    ResourceDoesNotExistError,
)
from app.models.domain.users import User

Record = Mapping[str, Any]


QUERY_DIR = Path(__file__).parent / "sql" / "users"
FIND_USER_BY_EMAIL = open(QUERY_DIR / "find_user_by_email.sql").read()
CREATE_USER = open(QUERY_DIR / "create_user.sql").read()
GET_HASHED_PASSWORD = open(QUERY_DIR / "get_hashed_password.sql").read()
GET_USER = open(QUERY_DIR / "get_user.sql").read()
UPDATE_USER = open(QUERY_DIR / "update_user.sql").read()


@dataclass(slots=True)
class UsersRepo(Singleton):
    pool: InjectDBConnectionPool

    async def find_user_by_email(self, email: str) -> User:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            user_row: Record | None = await conn.fetchrow(FIND_USER_BY_EMAIL, email)  # type: ignore  # for Pylance
        if user_row:
            return User(**user_row)
        raise ResourceDoesNotExistError

    async def get_user(self, user_id: UUID) -> User:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            user_row: Record | None = await conn.fetchrow(GET_USER, user_id)  # type: ignore  # for Pylance
        if user_row:
            return User(**user_row)
        raise ResourceDoesNotExistError

    async def create_user(
        self,
        *,
        username: str,
        email: str,
        hashed_password: str,
    ) -> User:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            try:
                user_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                    CREATE_USER,
                    username,
                    email,
                    hashed_password,
                )
            except asyncpg.UniqueViolationError as e:
                raise ResourceAlreadyExists from e
            return User(
                id=user_record["id"],
                username=username,
                email=email,
                image=None,
                bio=None,
                hashed_password=hashed_password,
            )

    async def update_user(
        self,
        *,
        current_user_id: UUID,  # from JWT
        username: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
        bio: str | None = None,
        image: str | None = None,
    ) -> User:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            user_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                UPDATE_USER,
                current_user_id,
                username,
                email,
                bio,
                image,
                hashed_password,
            )
            return User(**user_record)
