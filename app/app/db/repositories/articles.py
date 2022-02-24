from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
import orjson
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool
from app.db.repositories.exceptions import (
    ResourceDoesNotExistError,
    UserIsNotAuthorizedError,
)
from app.models.domain.articles import Article
from app.models.domain.comments import Comment
from app.models.domain.profiles import Profile

Record = Mapping[str, Any]


QUERY_DIR = Path(__file__).parent / "sql" / "articles"
CREATE_ARTICLE = open(QUERY_DIR / "create_article.sql").read()
ADD_COMMENT = open(QUERY_DIR / "add_comment.sql").read()
DELETE_ARTICLE = open(QUERY_DIR / "delete_article.sql").read()
FAVORITE_ARTICLE = open(QUERY_DIR / "favorite_article.sql").read()
UNFAVORITE_ARTICLE = open(QUERY_DIR / "unfavorite_article.sql").read()
GET_ARTICLE = open(QUERY_DIR / "get_article.sql").read()
SEARCH_ARTICLES = open(QUERY_DIR / "search_articles.sql").read()
UPDATE_ARTICLE = open(QUERY_DIR / "update_article.sql").read()


def _article_from_record(record: Record) -> Article:
    return Article(
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


@dataclass(slots=True)
class ArticlesRepo(Singleton):
    pool: InjectDBConnectionPool

    async def create_article(
        self,
        *,
        author_id: UUID,
        title: str,
        description: str,
        body: str,
        tags: list[str] | None,
    ) -> Article:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                CREATE_ARTICLE,
                author_id,
                title,
                description,
                body,
                tags or [],
            )

        return _article_from_record(
            {
                **article_record,
                "title": title,
                "description": description,
                "body": body,
                "tags": tags,
                "favorited": False,
                "favorites_count": 0,
            }
        )

    async def get_article_by_id(
        self,
        *,
        article_id: UUID,
        current_user_id: UUID | None,
    ) -> Article:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                GET_ARTICLE,
                current_user_id,
                article_id,
            )
        if article_record:
            return _article_from_record(article_record)
        raise ResourceDoesNotExistError

    async def list_articles(
        self,
        *,
        current_user_id: UUID | None,
        tag: str | None,
        author_username: str | None,
        favorited_by_username: str | None,
        limit: int,
        offset: int,
    ) -> list[Article]:
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
        return [_article_from_record(record) for record in article_records]

    async def favorite_article(
        self, *, current_user_id: UUID, article_id: UUID
    ) -> Article:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                FAVORITE_ARTICLE,
                current_user_id,
                article_id,
            )
            if article_record:
                return _article_from_record(article_record)
            raise ResourceDoesNotExistError

    async def unfavorite_article(
        self, *, current_user_id: UUID, article_id: UUID
    ) -> Article:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                UNFAVORITE_ARTICLE,
                current_user_id,
                article_id,
            )
            if article_record:
                return _article_from_record(article_record)
            raise ResourceDoesNotExistError

    async def delete_article(self, *, current_user_id: UUID, article_id: UUID) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            deletion_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                DELETE_ARTICLE,
                current_user_id,
                article_id,
            )
            if deletion_record["article_deleted"] is False:
                if deletion_record["article_exists"] is False:
                    raise ResourceDoesNotExistError
                raise UserIsNotAuthorizedError

    async def update_article(
        self,
        *,
        current_user_id: UUID,
        article_id: UUID,
        title: str | None,
        description: str | None,
        body: str | None,
    ) -> Article:
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
                raise ResourceDoesNotExistError
            owns: bool = article_record["current_user_owns_article"]
            if not owns:
                raise UserIsNotAuthorizedError
            return _article_from_record(article_record)

    async def add_comment_to_article(
        self,
        *,
        current_user_id: UUID,
        article_id: UUID,
        body: str,
    ) -> Comment:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            comment_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                ADD_COMMENT,
                current_user_id,
                article_id,
                body,
            )
            return Comment(
                id=comment_record["id"],
                created_at=comment_record["created_at"],
                updated_at=comment_record["updated_at"],
                body=body,
                author=Profile(
                    **orjson.loads(comment_record["author"]), following=False
                ),
            )
