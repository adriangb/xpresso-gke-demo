import random
import string
from typing import AsyncGenerator

import asyncpg  # type: ignore[import]
import pytest
from pydantic import SecretStr

from app.config import DatabaseConfig
from app.db.migrations import run as migrations  # type: ignore[import]
from tests.app import app


class Config(DatabaseConfig):
    db_username: str = "postgres"
    db_password: SecretStr = SecretStr("postgres")
    db_host: str = "localhost"
    db_port: int = 5432
    db_database_name: str = "postgres"


@pytest.fixture(scope="session")
async def admin_db_connection(
    anyio_backend: str,
) -> AsyncGenerator[asyncpg.Connection, None]:
    """Connection used to create test databases"""
    db_config = Config()
    conn: asyncpg.Connection = await asyncpg.connect(  # type: ignore
        user=db_config.db_username,
        password=db_config.db_password.get_secret_value(),
        database=db_config.db_database_name,
        port=db_config.db_port,
        host=db_config.db_host,
    )
    try:
        yield conn
    finally:
        await conn.close()  # type: ignore
    return


@pytest.fixture
async def app_db_pool(
    admin_db_connection: asyncpg.Connection,
) -> AsyncGenerator[asyncpg.Pool, None]:
    db_config = Config()
    # use a unique name so we don't need to clean up
    # and are independant of any other running tests
    db_name = "".join(random.choices(string.ascii_lowercase, k=16))
    await admin_db_connection.execute(f"CREATE DATABASE {db_name}")  # type: ignore  # for Pylance
    from time import time

    start = time()
    async with asyncpg.create_pool(  # type: ignore
        # we don't need concurrency for tests
        min_size=1,
        max_size=1,
        user=db_config.db_username,
        password=db_config.db_password.get_secret_value(),
        database=db_name,
        port=db_config.db_port,
        host=db_config.db_host,
    ) as app_pool:
        print(f"Took {time()-start:.2f} sec to create pool")
        conn: asyncpg.Connection
        async with app_pool.acquire() as conn:  # type: ignore
            await migrations.run(conn)
        with app.dependency_overrides as overrides:
            overrides[asyncpg.Pool] = lambda: app_pool
            yield app_pool
