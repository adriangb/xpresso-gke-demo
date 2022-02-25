import asyncio

import uvicorn  # type: ignore[import]
from starlette.middleware.cors import CORSMiddleware
from xpresso import App
from xpresso.middleware import Middleware

from app.config import AppConfig
from app.logconfig import get_json_logconfig
from app.routes import routes


def create_app(version: str) -> App:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_headers=["*"],
            allow_methods=["*"],
        )
    ]
    return App(routes=routes, middleware=middleware, version=version, title="Conduit")


async def main() -> None:
    # load config
    app_config = AppConfig()  # type: ignore  # values are loaded from env vars

    app = create_app(version=app_config.version)

    # set up JSON logging
    log_config = get_json_logconfig(app_config.log_level)

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
