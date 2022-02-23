import asyncio

import asyncpg  # type: ignore[import]
import uvicorn  # type: ignore[import]
from xpresso import App

from app.config import AppConfig, DatabaseConfig
from app.db.connection import get_pool
from app.db.migrations import run as migrations
from app.logconfig import get_json_logconfig
from app.routes import routes

app = App(routes=routes)


async def main() -> None:
    # load configs from the environment
    app_config = AppConfig()  # type: ignore  # values are loaded from env vars
    db_config = DatabaseConfig()  # type: ignore  # values are loaded from env vars

    # set up JSON logging
    log_config = get_json_logconfig(app_config.log_level)

    # get a database pool for the lifetime of the app
    async with get_pool(db_config) as pool:
        # run migrations
        conn: asyncpg.Connection
        async with pool.acquire() as conn:
            await migrations.run(conn)

        # bind that pool to the DI container
        app.dependency_overrides[asyncpg.Pool] = lambda: pool

        # start the server
        server_config = uvicorn.Config(
            app,
            port=app_config.app_port,
            host=app_config.app_host,
            log_config=log_config,
        )
        server = uvicorn.Server(server_config)
        await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
