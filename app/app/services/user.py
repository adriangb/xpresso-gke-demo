from dataclasses import asdict, dataclass
from typing import Annotated

from xpresso import Depends, HTTPException, status

from app.db.repositories.users import InjectUsersRepo, UserInDB
from app.models.schemas.auth import Unauthorized
from app.models.schemas.jwt import Token
from app.services.auth import InjectAuthService

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


@dataclass(slots=True)
class UsersService:
    auth_service: InjectAuthService
    users_repo: InjectUsersRepo

    async def get_current_user(self, authorization: str) -> LoggedInUser:
        token = extract_token_from_authroization_header(authorization)
        user_id = self.auth_service.verify_access_token_and_extract_user_id(token)
        maybe_user_in_db = await self.users_repo.get_user_by_id(id=user_id)
        if maybe_user_in_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Unauthorized.construct(reason="Invalid credentials"),
            )
        return LoggedInUser(**asdict(maybe_user_in_db), token=token)


InjectUsersService = Annotated[UsersService, Depends(scope="app")]
