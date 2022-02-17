from dataclasses import dataclass
from uuid import UUID

import asyncpg  # type: ignore[import]
import asyncpg.exceptions  # type: ignore[import]

from app.db.connection import InjectDBConnectionPool

DELETE_COMMENT_BY_ID = """\
DELETE FROM commnets WHERE id = $1;
"""


@dataclass(frozen=True, slots=True, eq=False)
class CommentsRepository:
    pool: InjectDBConnectionPool

    async def delete_comment(self, id: UUID) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore # For Pylance
            await conn.execute(DELETE_COMMENT_BY_ID)  # type: ignore # For Pylance
