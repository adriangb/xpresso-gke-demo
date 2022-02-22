from dataclasses import asdict, dataclass
from functools import partial
from typing import Annotated

from xpresso import Depends, FromHeader, HTTPException, status

from app.db.repositories.users import UserInDB, UsersRepository
from app.models.schemas.auth import Unauthorized
from app.models.schemas.jwt import Token
from app.services.auth import AuthService

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail={"Invalid authentication"}
)
PREFIX = "Token "
PREFIX_LENGTH = len(PREFIX)


def extract_token_from_authroization_header(authorization_header: str) -> Token:
    if not authorization_header.startswith(PREFIX):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Unauthorized.construct(
                reason="Invalid scheme in Authorization header"
            ),
        )
    return Token(authorization_header[PREFIX_LENGTH:])


@dataclass(slots=True, frozen=True)
class LoggedInUser(UserInDB):
    token: Token


async def get_current_user(
    auth_service: AuthService,
    users_repo: UsersRepository,
    required: bool,
    authorization: FromHeader[str | None] = None,
) -> LoggedInUser | None:
    if not authorization:
        if required:
            raise UNAUTHORIZED
        else:
            return None
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    maybe_user_in_db = await users_repo.get_user_by_id(id=user_id)
    if maybe_user_in_db is None and required:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Unauthorized.construct(reason="Invalid credentials"),
        )
    return LoggedInUser(**asdict(maybe_user_in_db), token=token)


RequireLoggedInUser = Annotated[
    LoggedInUser, Depends(partial(get_current_user, required=True))
]
OptionalLoggedInUser = Annotated[
    LoggedInUser | None, Depends(partial(get_current_user, required=False))
]
