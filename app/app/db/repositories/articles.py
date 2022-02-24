from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
import orjson
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool
from app.models.domain.articles import Article
from app.models.domain.comments import Comment
from app.models.domain.profiles import Profile

Record = Mapping[str, Any]


class ArticleNotFoundError(Exception):
    pass

class UserDoesNotOwnResourceError(Exception):
    pass


QUERY_DIR = Path(__file__).parent / "sql" / "articles"
CREATE = open(QUERY_DIR / "create.sql").read()
ADD_COMMENT = open(QUERY_DIR / "add_comment.sql").read()
DELETE_COMMENT = open(QUERY_DIR / "delete_comment.sql").read()
DELETE = open(QUERY_DIR / "delete.sql").read()
FAVORITE = open(QUERY_DIR / "favorite.sql").read()
UNFAVORITE = open(QUERY_DIR / "unfavorite.sql").read()
GET = open(QUERY_DIR / "get.sql").read()
SEARCH = open(QUERY_DIR / "search.sql").read()
UPDATE = open(QUERY_DIR / "update.sql").read()


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

    async def create_article(  # noqa: WPS211
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
                CREATE,
                author_id,
                title,
                description,
                body,
            )
            if tags:
                article_id = article_record["id"]
                records = [(article_id, tag) for tag in tags]
                await conn.executemany(LINK_TAGS_TO_ARTICLE, records)  # type: ignore  # for Pylance

        return _article_from_record(article_record)

    async def get_article_by_id(
        self,
        *,
        article_id: UUID,
        current_user_id: UUID | None,
    ) -> Article:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                GET,
                current_user_id,
                article_id,
            )
        if article_record:
            return _article_from_record(article_record)
        raise ArticleNotFoundError

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
                SEARCH,
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
                FAVORITE,
                current_user_id,
                article_id,
            )
            if article_record:
                return _article_from_record(article_record)
            raise ArticleNotFoundError

    async def unfavorite_article(
        self, *, current_user_id: UUID, article_id: UUID
    ) -> Article:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            article_record: Record | None = await conn.fetchrow(  # type: ignore  # for Pylance
                UNFAVORITE,
                current_user_id,
                article_id,
            )
            if article_record:
                return _article_from_record(article_record)
            raise ArticleNotFoundError

    async def delete_article(self, *, current_user_id: UUID, article_id: UUID) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            deletion_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                DELETE,
                current_user_id,
                article_id,
            )
            if deletion_record["article_exists"] is False:
                raise ArticleNotFoundError
            if deletion_record["deleted"] is False:
                raise UserDoesNotOwnResourceError

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
                UPDATE,
                current_user_id,
                article_id,
                title,
                description,
                body,
            )
            if article_record is None:
                raise ArticleNotFoundError
            owns: bool = article_record["current_user_owns_article"]
            if not owns:
                raise UserDoesNotOwnResourceError
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
                raise Comment

    async def get_comments_for_article(
        self,
        *,
        current_user_id: UUID | None,
        article_id: UUID,
    ) -> list[Comment]:
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
