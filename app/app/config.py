from typing import Literal

from pydantic import BaseSettings, SecretStr


class AppConfig(BaseSettings):
    app_port: int
    app_host: str
    log_level: Literal["DEBUG", "INFO"]


class DatabaseConfig(BaseSettings):
    db_username: str
    db_password: SecretStr | None = None
    db_host: str
    db_port: int
    db_database_name: str
