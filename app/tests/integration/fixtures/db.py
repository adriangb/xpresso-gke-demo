from typing import AsyncGenerator

import asyncpg  # type: ignore[import]
import pytest

from app.db.migrations import run as migrations  # type: ignore[import]
from app.main import app

# this makes postgres an in-memory db to speed up tests
RUN_POSTGRES_COMMAND = "docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres --mount type=tmpfs,destination=/var/lib/postgresql/data postgres"


@pytest.fixture(scope="session")
async def db_connection_pool(anyio_backend: str) -> AsyncGenerator[asyncpg.Pool, None]:
    try:
        async with asyncpg.create_pool(  # type: ignore
            user="postgres",
            password="postgres",
            database="postgres",
            port=5432,
            host="localhost",
        ) as pool:
            yield pool
    except OSError as e:
        # Probably Postgres is not running
        raise RuntimeError(
            "It seems like postgres is not running."
            "\n You can run it locally with docker."
            "\n On MacOS or Linux:"
            f"\n  {RUN_POSTGRES_COMMAND}"
        ) from e


@pytest.fixture(scope="session")
async def admin_db_connection(
    db_connection_pool: asyncpg.Pool,
) -> AsyncGenerator[asyncpg.Connection, None]:
    conn: asyncpg.Connection
    async with db_connection_pool.acquire() as conn:
        yield conn


@pytest.fixture
async def app_db_pool(
    db_connection_pool: asyncpg.Pool,
    admin_db_connection: asyncpg.Connection,
) -> AsyncGenerator[asyncpg.Pool, None]:
    await admin_db_connection.execute(
        "DROP SCHEMA public CASCADE;CREATE SCHEMA public;"
    )
    await migrations.run(admin_db_connection)
    with app.dependency_overrides as overrides:
        overrides[asyncpg.Pool] = lambda: db_connection_pool
        yield db_connection_pool
