from datetime import timedelta

import pytest
from app.services.auth import AuthService


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService(secret_key="foobarbaz", expiration_timedelta=timedelta(days=1))
