from dataclasses import dataclass
from typing import Annotated

import asyncpg  # type: ignore[import]
from xpresso import Depends

from app.db.connection import InjectDBConnectionPool

GET_ALL_TAGS = """select array(select tag_name from tags);"""


@dataclass(slots=True)
class TagsRepository:
    pool: InjectDBConnectionPool

    async def get_tags(self) -> list[str]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore # For Pylance
            return await conn.fetchval(GET_ALL_TAGS)  # type: ignore # For Pylance


InjectTagsRepo = Annotated[TagsRepository, Depends(scope="app")]
