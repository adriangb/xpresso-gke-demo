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
from app.models.domain.comments import Comment
from app.models.domain.profiles import Profile

Record = Mapping[str, Any]


QUERY_DIR = Path(__file__).parent / "sql" / "comments"
DELETE_COMMENT = open(QUERY_DIR / "delete_comment.sql").read()
GET_COMMENTS = open(QUERY_DIR / "get_comments.sql").read()


@dataclass(slots=True)
class CommentsRepo(Singleton):
    pool: InjectDBConnectionPool

    async def delete_comment(
        self,
        *,
        current_user_id: UUID,
        comment_id: UUID,
    ) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            deletion_record: Record = await conn.fetchrow(  # type: ignore  # for Pylance
                DELETE_COMMENT,
                current_user_id,
                comment_id,
            )
            if deletion_record["comment_deleted"] is False:
                if deletion_record["comment_exists"] is False:
                    raise ResourceDoesNotExistError
                raise UserIsNotAuthorizedError

    async def get_comments_for_article(
        self,
        *,
        current_user_id: UUID | None,
        article_id: UUID,
    ) -> list[Comment]:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore  # for Pylance
            comment_records: list[Record] = await conn.fetch(  # type: ignore  # for Pylance
                GET_COMMENTS,
                current_user_id,
                article_id,
            )
            return [
                Comment(
                    id=comment_record["id"],
                    created_at=comment_record["created_at"],
                    updated_at=comment_record["updated_at"],
                    body=comment_record["body"],
                    author=Profile(**orjson.loads(comment_record["author"])),
                )
                for comment_record in comment_records
            ]
