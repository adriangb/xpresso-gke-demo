import random

from httpx import AsyncClient, Response

from tests.integration.conftest import RegistedUserWithToken


async def test_follow(
    test_client: AsyncClient, registered_users_with_tokens: list[RegistedUserWithToken]
) -> None:
    follower = random.choice(registered_users_with_tokens)
    following = next(u for u in registered_users_with_tokens if u is not follower)
    expected_response = {
        "profile": {
            "username": following.user.username,
            "bio": following.user.bio,
            "image": following.user.image,
            "following": True,
        }
    }
    resp: Response = await test_client.post(
        f"/api/profiles/{following.user.username}/follow",
        headers={"Authorization": f"Token {follower.token}"},
    )
    assert resp.status_code == 200, resp.content
    assert resp.json() == expected_response
