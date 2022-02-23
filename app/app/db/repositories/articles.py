from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
import orjson
from xpresso.dependencies.models import Singleton

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


# $1: current user's ID
_ARTICLE_FIELDS = """\
    articles.id,
    articles.title,
    articles.description,
    articles.body,
    articles.created_at,
    articles.updated_at,
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
"""


GET_ARTICLE_BY_ID = f"""\
SELECT
{_ARTICLE_FIELDS}
FROM articles
WHERE id = $2
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

    @classmethod
    def from_record(cls, record: Record) -> "ArticleInDB":
        return ArticleInDB(
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


# $1 = current user's ID, maybe null
# $2 = tag filter, maybe null
# $3 = username filter, maybe null
# $4 = favorited username filter, maybe null
# $5 = limit
# $6 = offset
# Note the explicit casts, they are needed to help PostgreSQL understand the types
SEARCH_ARTICLES = f"""\
WITH matched_tags AS (
        SELECT article_id, tag_name FROM articles_to_tags
        WHERE $2::text IS NOT NULL AND tag_name = $2::text
    ), filter_author AS (
        SELECT id FROM users
        WHERE ($3::text IS NOT NULL AND username = $3::text)
    ), articles_favorited_by_filter_user AS (
        SELECT articles.id
        FROM users
        LEFT JOIN favorites ON (favorites.user_id = users.id)
        LEFT JOIN articles ON (favorites.article_id = articles.id)
        WHERE ($4::text IS NOT NULL AND users.username = $4::text)
    )
SELECT
{_ARTICLE_FIELDS}
FROM articles
WHERE (
    ($2::text IS NULL OR id IN (SELECT article_id FROM matched_tags))
    AND
    ($3::text IS NULL OR author_id IN (SELECT id FROM filter_author))
    AND
    ($4::text IS NULL OR id IN (SELECT id FROM articles_favorited_by_filter_user))
)
ORDER BY created_at DESC
LIMIT $5
OFFSET $6
"""

# $1 = current user's ID, maybe null
# $5 = limit
# $6 = offset
GET_ARTICLES_AUTHORED_BY_FOLOWEES = f"""\
SELECT
{_ARTICLE_FIELDS}
FROM articles
INNER JOIN followers_to_followings ON (follower_id = $1 AND following_id = articles.author_id)
ORDER BY created_at DESC
LIMIT $2
OFFSET $3
"""

# $1 = current user's ID
FAVORITE_ARTICLE = """\
INSERT INTO favorites (user_id, article_id) VALUES ($1, $2)
ON CONFLICT DO NOTHING
RETURNING 1
"""

# $1 = current user's ID
UNFAVORITE_ARTICLE = """\
DELETE FROM favorites
WHERE user_id = $1 and article_id = $2
RETURNING 1
"""

# $1 = current user's ID, maybe null
DELETE_ARTICLE = """\
DELETE FROM articles
WHERE author_id = $1 AND id = $2
"""


class ArticleNotFound(Exception):
    pass


# $1 = current user's ID
UPDATE_ARTICLE = f"""\
UPDATE articles
SET title        = COALESCE($3, title),
    description  = COALESCE($4, description),
    body         = COALESCE($5, body)
WHERE author_id = $1 AND id = $2
RETURNING
{_ARTICLE_FIELDS}
"""

# $1 = current user's ID
# $2 = comment ID
DELETE_COMMENT = """\
DELETE FROM commnets
WHERE author_id = $1 AND id = $2
"""

# $1 = current user's ID
# $2 = article_id
# $3 = comment body
CREATE_COMMENT = """\
WITH created_comment AS (
    INSERT INTO comments (author_id, article_id, body) VALUES ($1, $2, $3)
    RETURNING id, created_at, updated_at
)
SELECT
    id,
    created_at,
    updated_at,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image
        )
        FROM users
        WHERE id = $1
    ) AS author
FROM created_comment
"""

# $1 = current user's ID, maybe null
# $2 = article_id
GET_COMMENTS_FOR_ARTICLE = """\
SELECT
    id,
    created_at,
    updated_at,
    body,
    (
        SELECT json_build_object(
            'username', username,
            'bio', bio,
            'image', image,
            'following', EXISTS(SELECT 1 FROM followers_to_followings WHERE $1::uuid IS NOT NULL AND follower_id = $1::uuid AND following_id = author_id)
        )
        FROM users
        WHERE id = comments.author_id
    ) AS author
FROM comments
"""


@dataclass(slots=True)
class CommentInDB:
    id: UUID
    created_at: datetime
    updated_at: datetime
    body: str
    author: ProfileInDB


class CommentNotFound(Exception):
    pass


@dataclass(frozen=True, slots=True)
class ArticlesRepo(Singleton):
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

    async def get_article_by_id(
        self,
        *,
        article_id: UUID,
        current_user_id: UUID | None,
    ) -> ArticleInDB:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                GET_ARTICLE_BY_ID,
                current_user_id,
                article_id,
            )
        if article_record:
            return ArticleInDB.from_record(article_record)
        raise ArticleNotFound

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
                SEARCH_ARTICLES,
                current_user_id,
                tag,
                author_username,
                favorited_by_username,
                limit,
                offset,
            )
        return [ArticleInDB.from_record(record) for record in article_records]

    async def get_articles_by_followed_users(
        self,
        current_user_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[ArticleInDB]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_records: list[Record] = await conn.fetch(  # type: ignore  # for Pylance
                GET_ARTICLES_AUTHORED_BY_FOLOWEES,
                current_user_id,
                limit,
                offset,
            )
        return [ArticleInDB.from_record(record) for record in article_records]

    async def favorite_article(
        self, *, current_user_id: UUID, article_id: UUID
    ) -> ArticleInDB:
        # to avoid concurrency issues when favoriting and counting favorites
        # in the same query, do this in 2 queries
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            await conn.execute(  # type: ignore  # for Pylance
                FAVORITE_ARTICLE,
                current_user_id,
                article_id,
            )
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                GET_ARTICLE_BY_ID,
                current_user_id,
                article_id,
            )
            if article_record:
                return ArticleInDB.from_record(article_record)
            raise ArticleNotFound

    async def unfavorite_article(
        self, *, current_user_id: UUID, article_id: UUID
    ) -> ArticleInDB:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            await conn.execute(  # type: ignore  # for Pylance
                UNFAVORITE_ARTICLE,
                current_user_id,
                article_id,
            )
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                GET_ARTICLE_BY_ID,
                current_user_id,
                article_id,
            )
            if article_record:
                return ArticleInDB.from_record(article_record)
            raise ArticleNotFound

    async def delete_article(self, *, current_user_id: UUID, article_id: UUID) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            res = await conn.execute(  # type: ignore  # for Pylance
                DELETE_ARTICLE,
                current_user_id,
                article_id,
            )
            if res == "DELETE 0":
                raise ArticleNotFound

    async def update_article(
        self,
        *,
        current_user_id: UUID,
        article_id: UUID,
        title: str | None,
        description: str | None,
        body: str | None,
    ) -> ArticleInDB:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                UPDATE_ARTICLE,
                current_user_id,
                article_id,
                title,
                description,
                body,
            )
            if article_record is None:
                raise ArticleNotFound
            return ArticleInDB.from_record(article_record)

    async def add_comment_to_article(
        self,
        *,
        current_user_id: UUID,
        article_id: UUID,
        body: str,
    ) -> CommentInDB:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            comment_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                CREATE_COMMENT,
                current_user_id,
                article_id,
                body,
            )
            return CommentInDB(
                id=comment_record["id"],
                created_at=comment_record["created_at"],
                updated_at=comment_record["updated_at"],
                body=body,
                author=ProfileInDB(
                    **orjson.loads(comment_record["author"]), following=False
                ),
            )

    async def delete_comment(
        self,
        *,
        current_user_id: UUID,
        comment_id: UUID,
    ) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            res = await conn.execute(  # type: ignore  # for Pylance
                DELETE_COMMENT,
                current_user_id,
                comment_id,
            )
            if res == "DELETE 0":
                raise CommentNotFound

    async def get_comments_for_article(
        self,
        *,
        current_user_id: UUID | None,
        article_id: UUID,
    ) -> list[CommentInDB]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            comment_records: list[Record] = await conn.fetchrow(  # type: ignore  # for Pylance
                GET_COMMENTS_FOR_ARTICLE,
                current_user_id,
                article_id,
            )
            return [
                CommentInDB(
                    id=comment_record["id"],
                    created_at=comment_record["created_at"],
                    updated_at=comment_record["updated_at"],
                    body=comment_record["body"],
                    author=ProfileInDB(**orjson.loads(comment_record["author"])),
                )
                for comment_record in comment_records
            ]
