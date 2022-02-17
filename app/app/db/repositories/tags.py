from dataclasses import dataclass
from typing import Any, Mapping

import asyncpg  # type: ignore[import]
import asyncpg.exceptions  # type: ignore[import]

from app.db.connection import InjectDBConnectionPool

Record = Mapping[str, Any]


GET_ALL_TAGS = """select tag_name from articles_to_tags group by tag_name;"""
CREATE_TAGS = """INSERT INTO tags(tag_name) VALUES ($1) ON CONFLICT DO NOTHING;"""


@dataclass(frozen=True, slots=True, eq=False)
class TagsRepository:
    pool: InjectDBConnectionPool

    async def get_tags(self) -> list[str]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore # For Pylance
            tags: list[Record] = await conn.fetch(GET_ALL_TAGS)  # type: ignore # For Pylance
        return [t["tag_name"] for t in tags]

    async def ensure_tags_exist(self, tags: list[str]) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore # For Pylance
            await conn.executemany(CREATE_TAGS, [(t,) for t in tags])  # type: ignore # For Pylance
