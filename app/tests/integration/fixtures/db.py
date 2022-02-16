import random
import string
from typing import AsyncGenerator

import asyncpg  # type: ignore[import]
import pytest

from app.config import DatabaseConfig
from app.db.migrations import run as migrations
from app.main import app

# this makes postgres an in-memory db to speed up tests
RUN_POSTGRES_COMMAND = "docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres --mount type=tmpfs,destination=/var/lib/postgresql/data postgres"


@pytest.fixture(scope="session")
async def admin_db_connection(anyio_backend: str) -> asyncpg.Connection:
    """Connection used to create test databases"""
    try:
        return await asyncpg.connect(  # type: ignore
            user="postgres",
            password="postgres",
            database="postgres",
            port=5432,
            host="localhost",
        )
    except OSError as e:
        # Probably Postgres is not running
        raise RuntimeError(
            "It seems like postgres is not running."
            "\n You can run it locally with docker."
            "\n On MacOS or Linux:"
            f"\n  {RUN_POSTGRES_COMMAND}"
        ) from e


@pytest.fixture
async def app_db_pool(
    admin_db_connection: asyncpg.Connection,
) -> AsyncGenerator[asyncpg.Pool, None]:
    # use a unique name so we don't need to clean up
    db_name = "".join(random.choices(string.ascii_lowercase, k=16))
    await admin_db_connection.execute(f"CREATE DATABASE {db_name} OWNER postgres")
    db_config = DatabaseConfig(
        db_username="postgres",
        db_password="postgres",  # type: ignore[arg-type]
        db_database_name=db_name,
        db_port=5432,
        db_host="localhost",
    )
    await migrations.main(db_config)
    async with asyncpg.create_pool(
        # we don't need concurrency for tests
        min_size=1,
        max_size=1,
        user="postgres",
        password="postgres",
        database=db_name,
        port=5432,
        host="localhost",
    ) as app_pool:
        with app.dependency_overrides as overrides:
            overrides[asyncpg.Pool] = lambda: app_pool
            yield app_pool
        print("I'm back!")
