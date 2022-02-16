import random
import string
from typing import AsyncGenerator

import asyncpg  # type: ignore[import]
import httpx
import pytest
from app.config import DatabaseConfig
from app.db.migrations import run as migrations
from app.main import app
from asgi_lifespan import LifespanManager
from xpresso import App

RUN_POSTGRES_COMMAND = "docker run --rm -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres --mount type=tmpfs,destination=/var/lib/postgresql/data postgres -c fsync=off"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def admin_db_pool(anyio_backend: str) -> AsyncGenerator[asyncpg.Pool, None]:
    """Create a connection pool that can be used by tests
    but also to create/destroy databases for the tests.
    """
    try:
        async with asyncpg.create_pool(
            # we don't need concurrency for tests
            min_size=1,
            max_size=1,
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


@pytest.fixture
async def app_db_pool(
    admin_db_pool: asyncpg.Pool,
) -> AsyncGenerator[asyncpg.Pool, None]:
    # use a unique name so we don't need to clean up
    db_name = "".join(random.choices(string.ascii_lowercase, k=16))
    conn: asyncpg.Connection
    async with admin_db_pool.acquire() as conn:
        await conn.execute(f"CREATE DATABASE {db_name} OWNER postgres")
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
        yield app_pool


@pytest.fixture
async def test_app(app_db_pool: asyncpg.Pool) -> AsyncGenerator[App, None]:
    with app.dependency_overrides as overrides:
        overrides[asyncpg.Pool] = lambda: app_db_pool
        async with LifespanManager(app):
            yield app


@pytest.fixture
async def test_client(test_app: App) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(app=test_app, base_url="http://example.com") as client:
        yield client
