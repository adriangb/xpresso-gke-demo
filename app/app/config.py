from typing import Literal

from pydantic import SecretStr
from xpresso.config import Config


class AuthConfig(Config):
    token_signing_key: SecretStr


class DatabaseConfig(Config):
    db_username: str
    db_password: SecretStr | None
    db_host: str
    db_port: int
    db_database_name: str


class AppConfig(Config):
    app_port: int
    app_host: str
    log_level: Literal["DEBUG", "INFO"]
    service_name: str
    env: str
    version: str
