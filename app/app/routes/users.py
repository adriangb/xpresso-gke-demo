from app.db.repositories.users import UsersRepository
from app.dependencies import PasswordHasher
from app.models.schemas.users import UserInCreate, UserInResponse, UserWithToken
from app.requests import OrJSON
from app.services.auth import AuthService


async def create_user(
    user: OrJSON[UserInCreate],
    repo: UsersRepository,
    hasher: PasswordHasher,
    auth: AuthService,
) -> UserInResponse:
    # register the user in the db
    user_id = await repo.create_user(
        username=user.user.username,
        email=user.user.email,
        hashed_password=hasher.hash(user.user.password),
    )
    # create a token for them
    token = auth.create_access_token(user_id=user_id)
    # craete and return the response user model
    return UserInResponse.construct(
        user=UserWithToken.construct(
            username=user.user.username,
            email=user.user.email,
            bio=None,
            image=None,
            token=token,
        )
    )
