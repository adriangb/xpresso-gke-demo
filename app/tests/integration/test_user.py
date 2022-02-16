import random

from httpx import AsyncClient, Response

from tests.integration.conftest import RegistedUserWithToken


async def test_get(
    test_client: AsyncClient, registered_users_with_tokens: list[RegistedUserWithToken]
) -> None:
    user = random.choice(registered_users_with_tokens)
    user_info = user.user.dict(by_alias=True, exclude={"id", "hashed_password"})
    user_info["token"] = user.token
    expected_response = {"user": user_info}
    resp: Response = await test_client.get(
        "/api/user", headers={"Authorization": f"Token {user.token}"}
    )
    assert resp.status_code == 200, resp.content
    assert resp.json() == expected_response


async def test_update(
    test_client: AsyncClient, registered_users_with_tokens: list[RegistedUserWithToken]
) -> None:
    user = random.choice(registered_users_with_tokens)
    user = random.choice(registered_users_with_tokens)
    user_info = user.user.dict(by_alias=True, exclude={"id", "hashed_password"})
    user_info["token"] = user.token
    user_info["username"] = "John Snow"
    expected_response = {"user": user_info}
    resp: Response = await test_client.put(
        "/api/user",
        json={"user": {"username": "John Snow"}},
        headers={"Authorization": f"Token {user.token}"},
    )
    assert resp.status_code == 200, resp.content
    assert resp.json() == expected_response
