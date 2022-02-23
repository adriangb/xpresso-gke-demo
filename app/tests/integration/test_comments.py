from datetime import datetime
from uuid import UUID

import pytest
from httpx import AsyncClient, Response
from pydantic import BaseModel

from app.db.repositories.articles import ArticlesRepo
from tests.integration.conftest import RegistedUserWithToken


@pytest.fixture
def author(
    registered_users_with_tokens: list[RegistedUserWithToken],
) -> RegistedUserWithToken:
    return registered_users_with_tokens[0]


class ResponseProfileValidator(BaseModel):
    username: str
    bio: str | None
    image: str | None
    following: bool


class ResponseCommentValidator(BaseModel):
    body: str
    createdAt: datetime
    updatedAt: datetime
    id: UUID
    author: ResponseProfileValidator


async def test_create_comment(
    test_client: AsyncClient,
    articles_repo: ArticlesRepo,
    author: RegistedUserWithToken,
) -> None:
    article = await articles_repo.create_article(
        author_id=author.id,
        title="How to train your dragon",
        description="Ever wonder how?",
        body="It takes a Jacobian",
        tags=["dragons", "training"],
    )

    payload = {"comment": {"body": "A comment!"}}

    resp: Response = await test_client.post(
        f"/api/articles/{article.id}/comments",
        headers={"Authorization": f"Token {author.token}"},
        json=payload,
    )
    assert resp.status_code == 201, resp.content
    ResponseCommentValidator.validate(resp.json()["comment"])
    assert resp.json()["comment"]["author"] == {
        "username": author.user.username,
        "bio": author.user.bio,
        "image": author.user.image,
        "following": False,
    }
