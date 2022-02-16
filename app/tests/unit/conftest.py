from typing import Generator

import pytest
from app.main import app
from app.services import auth
from xpresso import App


@pytest.fixture
def test_app() -> Generator[App, None, None]:
    auth_service = auth.AuthService(secret_key="foobar")
    with app.dependency_overrides as overrides:
        overrides[auth.AuthService] = lambda: auth_service
        yield app
