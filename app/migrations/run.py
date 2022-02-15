import asyncio
import pathlib

from app.config import DatabaseConfig
from migri import PostgreSQLConnection, apply_migrations  # type: ignore[import]


async def main() -> None:
    config = DatabaseConfig()  # type: ignore  # arguments come from env
    if config.db_password:
        password = config.db_password.get_secret_value()
    else:
        password = None
    conn = PostgreSQLConnection(
        config.db_database_name,
        db_user=config.db_username,
        db_pass=password,
        db_host=config.db_host,
        db_port=config.db_port,
    )
    dir = (pathlib.Path(__file__).parent / "versions").absolute()
    async with conn:
        await apply_migrations(str(dir), conn)


if __name__ == "__main__":
    asyncio.run(main())
