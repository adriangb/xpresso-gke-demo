from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
import orjson
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool
from app.models.domain.articles import Article
from app.models.domain.profiles import Profile

Record = Mapping[str, Any]


QUERY_DIR = Path(__file__).parent / "sql" / "feed"
GET_FEED = open(QUERY_DIR / "get_feed.sql").read()


@dataclass(slots=True)
class FeedRepo(Singleton):
    pool: InjectDBConnectionPool

    async def get_feed(
        self,
        current_user_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[Article]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_records: list[Record] = await conn.fetch(  # type: ignore  # for Pylance
                GET_FEED,
                current_user_id,
                limit,
                offset,
            )
        return [
            Article(
                id=record["id"],
                title=record["title"],
                description=record["description"],
                body=record["body"],
                author=Profile(**orjson.loads(record["author"])),
                created_at=record["created_at"],
                updated_at=record["updated_at"],
                favorited=record["favorited"],
                favorites_count=record["favorites_count"],
                tags=record["tags"],
            )
            for record in article_records
        ]
