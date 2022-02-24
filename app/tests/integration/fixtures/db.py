import random
import string
from time import time
from typing import AsyncGenerator

import anyio
import asyncpg  # type: ignore[import]
import pytest
from pydantic import SecretStr

from app.config import DatabaseConfig
from app.db.migrations import run as migrations  # type: ignore[import]
from app.main import app

# this makes postgres an in-memory db to speed up tests
RUN_POSTGRES_COMMAND = "docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres --mount type=tmpfs,destination=/var/lib/postgresql/data postgres"

DB_CONNECT_TIMEOUT = 10


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
    config = Config()  # type: ignore
    start = time()
    while time() - start < DB_CONNECT_TIMEOUT:
        try:
            print(config.json())
            conn: asyncpg.Connection = await asyncpg.connect(  # type: ignore
                user=config.db_username,
                password=config.db_password.get_secret_value(),
                database=config.db_database_name,
                port=config.db_port,
                host=config.db_host,
            )
            print("connected")
            try:
                yield conn
            finally:
                await conn.close()  # type: ignore
            return
        except Exception as e:
            if time() - start < DB_CONNECT_TIMEOUT:
                await anyio.sleep(1)
                continue
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
    # and are independant of any other running tests
    db_name = "".join(random.choices(string.ascii_lowercase, k=16))
    await admin_db_connection.execute(f"CREATE DATABASE {db_name}")  # type: ignore  # for Pylance
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
