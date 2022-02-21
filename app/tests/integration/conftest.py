from dataclasses import asdict, dataclass
from typing import Generator

import pytest
from xpresso import App

from app.db.repositories.users import UsersRepository
from app.main import app
from app.services.auth import AuthService
from tests.integration.fixtures.repos import RegisterdUser


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
    users_repo: UsersRepository,
    auth_service: AuthService,
) -> Generator[App, None, None]:
    with app.dependency_overrides as overrides:
        overrides[UsersRepository] = lambda: users_repo
        overrides[AuthService] = lambda: auth_service
        yield app
