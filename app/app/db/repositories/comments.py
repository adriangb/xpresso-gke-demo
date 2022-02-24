from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import UUID

import asyncpg  # type: ignore[import]
from xpresso.dependencies.models import Singleton

from app.db.connection import InjectDBConnectionPool

Record = Mapping[str, Any]


class CommentNotFound(Exception):
    pass


QUERY_DIR = Path(__file__).parent / "sql" / "comments"
DELETE_COMMENT = open(QUERY_DIR / "delete_comment.sql").read()

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
            res = await conn.execute(  # type: ignore  # for Pylance
                DELETE_COMMENT,
                current_user_id,
                comment_id,
            )
            if res == "DELETE 0":
                raise CommentNotFound
