from dataclasses import asdict, dataclass
from typing import Generator

import pytest
from xpresso import App

from app.db.repositories.users import UsersRepo
from app.main import app
from app.services.auth import AuthService
from tests.integration.fixtures.client import test_client
from tests.integration.fixtures.db import admin_db_connection, app_db_pool
from tests.integration.fixtures.repos import (
    RegisterdUser,
    articles_repo,
    registered_users,
    users_repo,
)
from tests.integration.fixtures.services import auth_service

__all__ = [
    "auth_service",
    "registered_users",
    "articles_repo",
    "app_db_pool",
    "admin_db_connection",
    "test_client",
    "users_repo",
]


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@dataclass
class RegistedUserWithToken(RegisterdUser):
    token: str


@pytest.fixture
def registered_users_with_tokens(
    auth_service: AuthService, registered_users: list[RegisterdUser]
) -> list[RegistedUserWithToken]:
    return [
        RegistedUserWithToken(
            **asdict(u),
            token=auth_service.create_access_token(user_id=u.id),
        )
        for u in registered_users
    ]


@pytest.fixture
def test_app(
    users_repo: UsersRepo,
    auth_service: AuthService,
) -> Generator[App, None, None]:
    with app.dependency_overrides as overrides:
        overrides[UsersRepo] = lambda: users_repo
        overrides[AuthService] = lambda: auth_service
        yield app
