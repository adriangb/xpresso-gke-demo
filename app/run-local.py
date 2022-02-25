import asyncio

import asyncpg  # type: ignore[import]
import uvicorn  # type: ignore[import]

from app.config import AppConfig, AuthConfig, DatabaseConfig
from app.db.connection import get_pool
from app.db.migrations import run as migrations
from app.main import create_app


async def main() -> None:
    app_config = AppConfig(
        app_port=8000,
        app_host="localhost",
        log_level="DEBUG",
        env="test",
        version=open("VERSION.txt").read(),
        service_name="Conduit",
    )
    db_config = DatabaseConfig(
        db_username="postgres",
        db_password="postgres",  # type: ignore[arg-type]
        db_host="localhost",
        db_port=5432,
        db_database_name="postgres",
    )
    auth_config = AuthConfig(token_signing_key="foobarbaz")  # type: ignore[arg-type]

    # create the app
    app = create_app(version=app_config.version)

    # bind configs to di container
    app.dependency_overrides[AppConfig] = lambda: app_config
    app.dependency_overrides[DatabaseConfig] = lambda: db_config
    app.dependency_overrides[AuthConfig] = lambda: auth_config

    # get a database pool for the lifetime of the app
    async with get_pool(db_config) as pool:
        # run migrations
        conn: asyncpg.Connection
        async with pool.acquire() as conn:  # type: ignore
            await migrations.run(conn)

        # bind that pool to the di container
        app.dependency_overrides[asyncpg.Pool] = lambda: pool

        # start the server
        server_config = uvicorn.Config(
            app,
            port=app_config.app_port,
            host=app_config.app_host,
        )
        server = uvicorn.Server(server_config)
        await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
