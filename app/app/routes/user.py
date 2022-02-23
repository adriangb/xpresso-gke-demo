from xpresso import FromJson

from app.db.repositories.users import InjectUsersRepo
from app.dependencies import PasswordHasher, RequireLoggedInUser
from app.models.schemas.users import UserInResponse, UserInUpdate, UserWithToken


async def get_user(current_user: RequireLoggedInUser) -> UserInResponse:
    # build and return the user model
    return UserInResponse.construct(
        user=UserWithToken.construct(
            username=current_user.username,
            email=current_user.email,
            bio=current_user.bio,
            image=current_user.image,
            token=current_user.token,
        )
    )


async def update_user(
    updated_user_info: FromJson[UserInUpdate],
    current_user: RequireLoggedInUser,
    repo: InjectUsersRepo,
    hasher: PasswordHasher,
) -> UserInResponse:
    user_info = updated_user_info.user
    # check if they are changing their password
    if user_info.password is not None:
        hashed_password = hasher.hash(user_info.password)
    else:
        hashed_password = None
    # update the user in the database
    await repo.update_user(
        id_of_current_user=current_user.id,
        username=user_info.username,
        email=user_info.email,
        hashed_password=hashed_password,
        bio=user_info.bio,
        image=user_info.image,
    )
    # build and return the user model
    return UserInResponse.construct(
        user=UserWithToken.construct(
            username=user_info.username or current_user.username,
            email=user_info.email or current_user.email,
            bio=user_info.bio if user_info.bio is not None else current_user.bio,
            image=current_user.image or current_user.image,
            token=current_user.token,
        )
    )
