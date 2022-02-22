import random
import string
from typing import AsyncGenerator

import asyncpg  # type: ignore[import]
import pytest

from app.db.migrations import run as migrations  # type: ignore[import]
from app.main import app

# this makes postgres an in-memory db to speed up tests
RUN_POSTGRES_COMMAND = "docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres --mount type=tmpfs,destination=/var/lib/postgresql/data postgres"


@pytest.fixture(scope="session")
async def admin_db_connection(
    anyio_backend: str,
) -> AsyncGenerator[asyncpg.Connection, None]:
    """Connection used to create test databases"""
    try:
        conn: asyncpg.Connection = await asyncpg.connect(  # type: ignore
            user="postgres",
            password="postgres",
            database="postgres",
            port=5432,
            host="localhost",
        )
        yield conn
    except OSError as e:
        # Probably Postgres is not running
        raise RuntimeError(
            "It seems like postgres is not running."
            "\n You can run it locally with docker."
            "\n On MacOS or Linux:"
            f"\n  {RUN_POSTGRES_COMMAND}"
        ) from e
    else:
        await conn.close()  # type: ignore


@pytest.fixture
async def app_db_pool(
    admin_db_connection: asyncpg.Connection,
) -> AsyncGenerator[asyncpg.Pool, None]:
    # use a unique name so we don't need to clean up
    # and are independant of any other running tests
    db_name = "".join(random.choices(string.ascii_lowercase, k=16))
    await admin_db_connection.execute(f"CREATE DATABASE {db_name}")
    async with asyncpg.create_pool(  # type: ignore
        # we don't need concurrency for tests
        min_size=1,
        max_size=1,
        user="postgres",
        password="postgres",
        database=db_name,
        port=5432,
        host="localhost",
    ) as app_pool:
        conn: asyncpg.Connection
        async with app_pool.acquire() as conn:  # type: ignore
            await migrations.run(conn)
        with app.dependency_overrides as overrides:
            overrides[asyncpg.Pool] = lambda: app_pool
            yield app_pool
