import random

from httpx import AsyncClient, Response
from tests.integration.conftest import RegistedUserWithToken


async def test_login(
    test_client: AsyncClient,
    registered_users_with_tokens: list[RegistedUserWithToken],
) -> None:
    user = random.choice(registered_users_with_tokens)
    expected_response = {
        "user": {
            **user.user.dict(by_alias=True, exclude={"id", "hashed_password"}),
            "token": user.token,
        }
    }

    payload = {"user": {"email": user.user.email, "password": user.password}}
    resp: Response = await test_client.post("/api/users/login", json=payload)
    assert resp.status_code == 200, resp.content
    received_response = resp.json()
    # tokens can be different
    expected_response["user"].pop("token")  # tokens can be different
    received_response["user"].pop("token")  # type: ignore
    assert received_response == expected_response
