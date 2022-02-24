from xpresso import FromJson

from app.db.repositories.users import UsersRepo
from app.dependencies import PasswordHasher
from app.models.schemas.users import UserInCreate, UserInResponse, UserWithToken
from app.services.auth import AuthService


async def create_user(
    user_info: FromJson[UserInCreate],
    repo: UsersRepo,
    hasher: PasswordHasher,
    auth: AuthService,
) -> UserInResponse:
    # register the user in the db
    user = await repo.create_user(
        username=user_info.user.username,
        email=user_info.user.email,
        hashed_password=hasher.hash(user_info.user.password),
    )
    # create a token for them
    token = auth.create_access_token(user_id=user.id)
    # craete and return the response user model
    return UserInResponse.construct(user=UserWithToken.from_domain_model(user, token))
