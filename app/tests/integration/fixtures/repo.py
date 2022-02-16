from typing import NamedTuple

import asyncpg  # type: ignore[import]
import pytest

from app.db.repositories import users
from app.models.domain.users import User
from tests.hasher import password_hasher


@pytest.fixture
async def users_repo(app_db_pool: asyncpg.Pool) -> users.UsersRepository:
    return users.UsersRepository(app_db_pool)


class RegisterdUser(NamedTuple):
    user: users.UserInDB
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
        res.append(RegisterdUser(user=db_user, password=password))

    return res
