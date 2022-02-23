import random

from httpx import AsyncClient, Response

from app.db.repositories.users import UsersRepo
from tests.integration.conftest import RegistedUserWithToken


async def test_get_profile_following(
    test_client: AsyncClient,
    registered_users_with_tokens: list[RegistedUserWithToken],
    users_repo: UsersRepo,
) -> None:
    follower = random.choice(registered_users_with_tokens)
    following = next(u for u in registered_users_with_tokens if u is not follower)
    await users_repo.follow_user(following.user.username, follower.id)

    expected_response = {
        "profile": {
            "username": following.user.username,
            "bio": following.user.bio,
            "image": following.user.image,
            "following": True,
        }
    }

    resp: Response = await test_client.get(
        f"/api/profiles/{following.user.username}",
        headers={"Authorization": f"Token {follower.token}"},
    )
    assert resp.status_code == 200, resp.content
    assert resp.json() == expected_response
