from typing import Generator

import pytest
from app.db.repositories.users import UserInDB, UsersRepository
from app.main import app
from app.models.schemas.users import UserWithToken
from app.services.auth import AuthService
from tests.integration.fixtures.client import test_client
from tests.integration.fixtures.db import admin_db_connection, app_db_pool
from tests.integration.fixtures.repo import registered_users, users_repo
from tests.integration.fixtures.services import auth_service
from xpresso import App

__all__ = (
    "test_client",
    "admin_db_connection",
    "app_db_pool",
    "registered_users",
    "users_repo",
    "auth_service",
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def registered_users_with_tokens(
    auth_service: AuthService, registered_users: list[UserInDB]
) -> list[UserWithToken]:
    return [
        UserWithToken(**u.dict(), token=auth_service.create_access_token(user_id=u.id))
        for u in registered_users
    ]


@pytest.fixture
def test_app(
    users_repo: UsersRepository,
    auth_service: AuthService,
) -> Generator[App, None, None]:
    with app.dependency_overrides as overrides:
        overrides[UsersRepository] = lambda: users_repo
        overrides[AuthService] = lambda: auth_service
        yield app
