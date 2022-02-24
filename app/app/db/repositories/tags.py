from dataclasses import dataclass
from pathlib import Path

import asyncpg  # type: ignore[import]
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool

QUERY_DIR = Path(__file__).parent / "sql" / "tags"
GET_ALL_TAGS = open(QUERY_DIR / "get_all_tags.sql").read()


@dataclass(slots=True)
class TagsRepo(Singleton):
    pool: InjectDBConnectionPool

    async def get_tags(self) -> list[str]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore # For Pylance
            return await conn.fetchval(GET_ALL_TAGS)  # type: ignore # For Pylance
