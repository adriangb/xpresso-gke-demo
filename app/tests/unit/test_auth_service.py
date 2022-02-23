from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.config import AuthConfig
from app.models.schemas.jwt import Token
from app.services.auth import AuthService, InvalidTokenError


def test_auth_service_create_token() -> None:
    user_id = UUID("e7d0470c-46a9-44aa-8e7e-42eef8d1222e")
    fixed_datetime = datetime(2022, 2, 18, tzinfo=timezone.utc)
    exptected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlN2QwNDcwYy00NmE5LTQ0YWEtOGU3ZS00MmVlZjhkMTIyMmUiLCJleHAiOjE2NDU3NDcyMDAuMH0.C7_eweY0IhWhgo3ixS0-HCZZF8r36-W0hdEaKnCRZIk"

    service = AuthService(AuthConfig(token_signing_key="foobarbaz"), now=lambda: fixed_datetime)  # type: ignore  # for Pylance
    created_token = service.create_access_token(user_id=user_id)

    assert created_token == exptected_token


def test_auth_service_get_id_from_token() -> None:
    expected_user_id = UUID("e7d0470c-46a9-44aa-8e7e-42eef8d1222e")
    # this token has an exp in 3021
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlN2QwNDcwYy00NmE5LTQ0YWEtOGU3ZS00MmVlZjhkMTIyMmUiLCJleHAiOjMzMTgxMDA4OTU2LjQzNzk5Mn0.YToq_m0fj2TNRQogFP7RAIb8dQfBQifRt4wLj-A9cZ0"

    service = AuthService(AuthConfig(token_signing_key="foobarbaz"))  # type: ignore  # for Pylance
    got_user_id = service.verify_access_token_and_extract_user_id(Token(token))

    assert got_user_id == expected_user_id


@pytest.mark.parametrize(
    "token",
    [
        "foobarbaz",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlN2QwNDcwYy00NmE5LTQ0YWEtOGU3ZS00MmVlZjhkMTIyMmUiLCJleHAiOjE2NDU2MTc0NzQuMDk0MTQxfQ.uXpiaXwFfDeGEAsgcLBbl78Xa7lYUkyiRJD52inbrnc",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlN2QwNDcwYy00NmE5LTQ0YWEtOGU3ZS00MmVlZjhkMTIyMmUiLCJleHAiOjU3Mjc0NTYwMC4wfQ.HhoD1FhWq01UFNJH8ukzSymlsyONVbTYUgWCL-0aNS0",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjMzMTgxMTQyNDAwLjB9.zfUv486SwzDHPL-BL8aedINQcgTNIKVcDw7BcgYc7fs",
    ],
    ids=["not a token", "different key", "expired", "invalid payload"],
)
def test_invalid_token(token: str) -> None:
    with pytest.raises(InvalidTokenError):
        service = AuthService(AuthConfig(token_signing_key="foobarbaz"))  # type: ignore  # for Pylance
        service.verify_access_token_and_extract_user_id(Token(token))
