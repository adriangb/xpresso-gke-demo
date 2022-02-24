from contextlib import asynccontextmanager
from dataclasses import dataclass
from logging import getLogger
from typing import Annotated, AsyncGenerator

import asyncpg  # type: ignore[import]
from xpresso import Depends
from xpresso.dependencies.models import Singleton

from app.config import DatabaseConfig

logger = getLogger(__name__)


async def _get_pool(config: DatabaseConfig) -> AsyncGenerator[asyncpg.Pool, None]:
    # password is optional:
    # - cloudsql proxy won't work with it
    # - docker run postgres won't work without it
    connection_kwargs = dict(
        host=config.db_host,
        port=config.db_port,
        database=config.db_database_name,
        user=config.db_username,
    )
    if config.db_password is not None:
        connection_kwargs["password"] = config.db_password.get_secret_value()
    logger.info(f"Attempting DB connection" f" using config {config.dict()}")
    async with asyncpg.create_pool(**connection_kwargs) as pool:  # type: ignore
        yield pool


get_pool = asynccontextmanager(_get_pool)


InjectDBConnectionPool = Annotated[asyncpg.Pool, Depends(_get_pool, scope="app")]


async def get_connection(
    pool: InjectDBConnectionPool,
) -> AsyncGenerator[asyncpg.Connection, None]:
    async with pool.acquire() as conn:  # type: ignore
        yield conn


InjectDBConnection = Annotated[asyncpg.Connection, Depends(get_connection)]


@dataclass(slots=True)
class ConnectionHealth(Singleton):
    pool: InjectDBConnectionPool

    async def is_connected(self) -> bool:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:  # type: ignore
            return await conn.fetchval("SELECT 1") == 1  # type: ignore
