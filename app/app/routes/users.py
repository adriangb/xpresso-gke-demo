from xpresso import FromJson, Path

from app.db.repositories.users import UsersRepository
from app.dependencies import PasswordHasher
from app.models.domain.users import User
from app.models.schemas.users import UserInCreate, UserInResponse


async def create_user(
    user: FromJson[UserInCreate], repo: UsersRepository, hasher: PasswordHasher
) -> UserInResponse:
    # register the user in the db
    await repo.create_user(
        username=user.user.username,
        email=user.user.email,
        hashed_password=hasher.hash(user.user.password),
    )
    # craete and return the response user model
    return UserInResponse.construct(
        user=User(
            username=user.user.username, email=user.user.email, bio=None, image=None
        )
    )


path_item = Path("/users", post=create_user)
