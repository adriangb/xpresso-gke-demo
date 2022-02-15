import asyncio

import uvicorn  # type: ignore[import]
from app.config import AppConfig, DatabaseConfig
from app.lifespan import lifespan
from app.logconfig import get_json_logconfig
from app.routes import routes
from xpresso import App

app = App(routes=routes, lifespan=lifespan)


async def main() -> None:
    app_config = AppConfig()  # type: ignore  # values are loaded from env vars
    db_config = DatabaseConfig()  # type: ignore  # values are loaded from env vars
    app.dependency_overrides[AppConfig] = lambda: app_config
    app.dependency_overrides[DatabaseConfig] = lambda: db_config
    log_config = get_json_logconfig(app_config.log_level)
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
