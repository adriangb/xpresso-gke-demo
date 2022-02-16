import random

from app.models.schemas.users import UserWithToken
from httpx import AsyncClient, Response


async def test_get(
    test_client: AsyncClient, registered_users_with_tokens: list[UserWithToken]
) -> None:
    user = random.choice(registered_users_with_tokens)
    expected_response = {"user": user.dict(by_alias=True)}
    resp: Response = await test_client.get(
        "/api/user", headers={"Authorization": f"Token {user.token}"}
    )
    assert resp.status_code == 200, resp.content
    assert resp.json() == expected_response


async def test_update(
    test_client: AsyncClient, registered_users_with_tokens: list[UserWithToken]
) -> None:
    user = random.choice(registered_users_with_tokens)
    user = random.choice(registered_users_with_tokens)
    expected_response = {
        "user": {
            **user.dict(by_alias=True),
            **{"username": "John Snow"},
        }
    }
    resp: Response = await test_client.put(
        "/api/user",
        json={"user": {"username": "John Snow"}},
        headers={"Authorization": f"Token {user.token}"},
    )
    assert resp.status_code == 200, resp.content
    assert resp.json() == expected_response
