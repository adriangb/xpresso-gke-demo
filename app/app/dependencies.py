from typing import Annotated

import argon2
from xpresso import Depends, FromHeader

from app.services.user import LoggedInUser, UserService

PasswordHasher = Annotated[
    argon2.PasswordHasher, Depends(lambda: argon2.PasswordHasher(), scope="app")
]


async def _require_logged_in_user(
    user_service: UserService, authorization: FromHeader[str]
) -> LoggedInUser:
    return await user_service.get_current_user(authorization)


async def _optional_logged_in_user(
    user_service: UserService, authorization: FromHeader[str | None] = None
) -> LoggedInUser | None:
    if authorization is None:
        return None
    return await user_service.get_current_user(authorization)


RequireLoggedInUser = Annotated[LoggedInUser, Depends(_require_logged_in_user)]
OptionalLoggedInUser = Annotated[LoggedInUser | None, Depends(_optional_logged_in_user)]
