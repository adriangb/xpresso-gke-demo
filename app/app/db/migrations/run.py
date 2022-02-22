import asyncio
import pathlib

import asyncpg  # type: ignore[import]
from migri import PostgreSQLConnection, apply_migrations  # type: ignore[import]

from app.config import DatabaseConfig


class FixedPostgreSQLConnection(PostgreSQLConnection):  # type: ignore[misc]
    async def disconnect(self) -> None:
        if self.connection is None:
            await super().disconnect()


async def run(asyncpg_connection: asyncpg.Connection) -> None:
    conn = FixedPostgreSQLConnection(connection=asyncpg_connection)
    dir = (pathlib.Path(__file__).parent / "versions").absolute()
    async with conn:
        await apply_migrations(str(dir), conn)


async def main() -> None:
    config = DatabaseConfig()  # type: ignore  # arguments come from env
    print("Connecting")
    if config.db_password:
        password = config.db_password.get_secret_value()
    else:
        password = None
    conn: asyncpg.Connection = await asyncpg.connect(  # type: ignore
        host=config.db_host,
        port=config.db_port,
        database=config.db_database_name,
        user=config.db_username,
        password=password,
    )
    print("Running migrations")
    try:
        await run(conn)
    finally:
        await conn.close()  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
