from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]

from app.db.connection import InjectDBConnectionPool

Record = Mapping[str, Any]


CREATE_ARTICLE = """\
WITH author_subquery AS (
    SELECT id
    FROM users
    WHERE id = $1
)
INSERT INTO articles (title, description, body, author_id)
VALUES ($2, $3, $4, (SELECT id FROM author_subquery))
RETURNING 
    id,
    title,
    description,
    body,
    (SELECT id FROM author_subquery) as author_id,
    created_at,
    updated_at;
"""

LINK_TAGS_TO_ARTICLE = """\
INSERT INTO articles_to_tags (article_id, tag_name) VALUES ($1, $2)
"""

@dataclass(frozen=True, slots=True, eq=False)
class ArticleInDB:
    id: UUID
    title: str
    description: str
    body: str
    author_id: UUID
    created_at: datetime
    updated_at: datetime


CREATE_TAGS = """INSERT INTO tags(tag_name) VALUES $1 ON CONFLICT DO NOTHING;"""


@dataclass(frozen=True, slots=True, eq=False)
class ArticlesRepository:
    pool: InjectDBConnectionPool

    async def create_article(  # noqa: WPS211
        self,
        *,
        author_id: UUID,
        title: str,
        description: str,
        body: str,
        tags: list[str] | None,
    ) -> ArticleInDB:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                CREATE_ARTICLE,
                author_id,
                title,
                description,
                body,
            )
            if tags:
                article_id = article_record["id"]
                records = [(article_id, tag) for tag in tags]
                await conn.executemany(LINK_TAGS_TO_ARTICLE, records)  # type: ignore  # for Pylance

        return ArticleInDB(**article_record)
