import pytest

from app.config import AuthConfig
from app.services.auth import AuthService


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService(AuthConfig(token_signing_key="foobarbaz"))  # type: ignore  # for Pylance
