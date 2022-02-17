from dataclasses import dataclass
from uuid import UUID

import asyncpg  # type: ignore[import]
import pytest

from app.db.repositories import followers, users
from app.models.domain.users import User
from tests.hasher import password_hasher


@pytest.fixture
async def users_repo(app_db_pool: asyncpg.Pool) -> users.UsersRepository:
    return users.UsersRepository(app_db_pool)


@dataclass
class RegisterdUser:
    user: User
    id: UUID
    hashed_password: str
    password: str


@pytest.fixture
async def registered_users(users_repo: users.UsersRepository) -> list[RegisterdUser]:
    us = [
        User(
            username="foo", email="foo@example.com", bio="foo goes to a bar", image=None
        ),
        User(
            username="bar",
            email="bar@example.com",
            bio=None,
            image="http://example.com/bar.jpg",
        ),
        User(username="baz", email="baz@example.com", bio="", image=None),
        User(username="ăѣծềģ", email="ăѣծềģ@example.com", bio="Ɍ", image=None),
    ]
    res: list[RegisterdUser] = []
    for u in us:
        password = u.username + u.email
        await users_repo.create_user(
            username=u.username,
            email=u.email,
            hashed_password=password_hasher.hash(password),
        )
        db_user = await users_repo.get_user_by_email(email=u.email)
        assert db_user is not None
        user = User(
            username=db_user.username,
            email=db_user.email,
            bio=db_user.bio,
            image=db_user.image,
        )
        res.append(
            RegisterdUser(
                user=user,
                password=password,
                id=db_user.id,
                hashed_password=db_user.hashed_password,
            )
        )

    return res


@pytest.fixture
async def followers_repo(app_db_pool: asyncpg.Pool) -> followers.FollowersRepository:
    return followers.FollowersRepository(app_db_pool)
