from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
import orjson

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
    created_at,
    updated_at;
"""

LINK_TAGS_TO_ARTICLE = """\
INSERT INTO articles_to_tags (article_id, tag_name) VALUES ($1, $2) ON CONFLICT DO NOTHING;
"""


@dataclass(frozen=True, slots=True)
class ArticleCreatedInDB:
    id: UUID
    created_at: datetime
    updated_at: datetime


GET_ARTICLE_BY_ID = """\
WITH users_that_favorited AS (
    SELECT user_id FROM favorites
    WHERE article_id = $1
)
SELECT (
    id,
    title,
    description,
    body,
    author_id,
    created_at,
    updated_at,
    EXISTS(SELECT 1 FROM users_that_favorited WHERE user_id = $2) AS favorited,
    COUNT(SELECT user_id FROM users_that_favorited) AS favorites_count
)
FROM articles
WHERE id = $1
"""


@dataclass(frozen=True, slots=True)
class ProfileInDB:
    username: str
    bio: str | None
    image: str | None
    following: bool


@dataclass(frozen=True, slots=True)
class ArticleInDB:
    id: UUID
    title: str
    description: str
    body: str
    author: ProfileInDB
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    favorited: bool
    favorites_count: int


# $1 = current user's ID, maybe null
# $2 = tag filter, maybe null
# $3 = username filter, maybe null
# $4 = favorited username filter, maybe null
# $5 = limit
# $6 = offset
# Note the explicit casts, they are needed to help PostgreSQL understand the types
FILTER_ARTICLES = """\
WITH matched_tags AS (
        SELECT article_id, tag_name FROM articles_to_tags
        WHERE $2::text IS NOT NULL AND tag_name = $2::text
    ), filter_author AS (
        SELECT id FROM users
        WHERE ($3::text IS NOT NULL AND username = $3::text)
    ), filter_favorited_by_user AS (
        SELECT id FROM users
        WHERE ($4::text IS NOT NULL AND username = $4::text)
    )
SELECT
    id,
    title,
    description,
    body,
    author_id,
    created_at,
    updated_at,
    EXISTS(SELECT 1 FROM favorites WHERE $1::uuid IS NOT NULL AND user_id = $1::uuid AND article_id = id) AS favorited,
    (SELECT COUNT(*) FROM favorites WHERE article_id = id) AS favorites_count,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image,
            'following', EXISTS(SELECT 1 FROM followers_to_followings WHERE $1::uuid IS NOT NULL AND follower_id = $1::uuid AND following_id = author_id)
        )
        FROM users
        WHERE id = author_id
    ) AS author,
    (SELECT array_agg(tag_name) FROM articles_to_tags WHERE article_id = id) AS tags
FROM articles
WHERE (
    ($2::text IS NULL OR id IN (SELECT article_id FROM matched_tags))
    AND
    ($3::text IS NULL OR author_id IN (SELECT id FROM filter_author))
    AND
    ($4::text IS NULL OR author_id IN (SELECT id FROM filter_favorited_by_user))
)
LIMIT $5
OFFSET $6
"""


@dataclass(frozen=True, slots=True)
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
    ) -> ArticleCreatedInDB:
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

        return ArticleCreatedInDB(**article_record)

    async def get_article_by_id(self, id: UUID) -> ArticleInDB | None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                GET_ARTICLE_BY_ID, id
            )
        if article_record:
            return ArticleInDB(**article_record)
        return None

    async def list_articles(
        self,
        *,
        current_user_id: UUID | None,
        tag: str | None,
        author_username: str | None,
        favorited_by_username: str | None,
        limit: int,
        offset: int,
    ) -> list[ArticleInDB]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_records: list[Record] = await conn.fetch(  # type: ignore  # for Pylance
                FILTER_ARTICLES,
                current_user_id,
                tag,
                author_username,
                favorited_by_username,
                limit,
                offset,
            )
        return [
            ArticleInDB(
                id=record["id"],
                title=record["title"],
                description=record["description"],
                body=record["body"],
                author=ProfileInDB(**orjson.loads(record["author"])),
                created_at=record["created_at"],
                updated_at=record["updated_at"],
                favorited=record["favorited"],
                favorites_count=record["favorites_count"],
                tags=record["tags"],
            )
            for record in article_records
        ]
