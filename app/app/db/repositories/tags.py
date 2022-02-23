from dataclasses import dataclass

import asyncpg  # type: ignore[import]
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool

GET_ALL_TAGS = """select array(select tag_name from tags);"""


@dataclass(slots=True)
class TagsRepo(Singleton):
    pool: InjectDBConnectionPool

    async def get_tags(self) -> list[str]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore # For Pylance
            return await conn.fetchval(GET_ALL_TAGS)  # type: ignore # For Pylance
