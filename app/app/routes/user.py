from app.db.repositories.users import UsersRepository
from app.dependencies import PasswordHasher
from app.models.schemas.auth import Unauthorized
from app.models.schemas.users import UserInResponse, UserInUpdate, UserWithToken
from app.routes.utils import extract_token_from_authroization_header
from app.services.auth import AuthService
from xpresso import FromHeader, FromJson, HTTPException, Path, status


async def get_user(
    authorization: FromHeader[str],
    auth_service: AuthService,
    repo: UsersRepository,
) -> UserInResponse:
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    # check that the user exists in the database
    maybe_user_in_db = await repo.get_user_by_id(id=user_id)
    if maybe_user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Unauthorized.construct(reason="Invalid credentials"),
        )
    # build and return the user model
    return UserInResponse.construct(
        user=UserWithToken.construct(
            username=maybe_user_in_db.username,
            email=maybe_user_in_db.email,
            bio=maybe_user_in_db.bio,
            image=maybe_user_in_db.image,
            token=token,
        )
    )


async def update_user(
    user_info: FromJson[UserInUpdate],
    authorization: FromHeader[str],
    auth_service: AuthService,
    repo: UsersRepository,
    hasher: PasswordHasher,
) -> UserInResponse:
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    # check that the user exists in the database
    maybe_user_in_db = await repo.get_user_by_id(id=user_id)
    if maybe_user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Unauthorized.construct(reason="Invalid credentials"),
        )
    # check if they are changing their password
    if user_info.password is not None:
        hashed_password = hasher.hash(user_info.password)
    else:
        hashed_password = None
    # update the user in the database
    await repo.update_user(
        user_id=user_id,
        username=user_info.username,
        email=user_info.email,
        hashed_password=hashed_password,
        bio=user_info.bio,
        image=user_info.image,
    )
    # build and return the user model
    return UserInResponse.construct(
        user=UserWithToken.construct(
            username=maybe_user_in_db.username,
            email=maybe_user_in_db.email,
            bio=maybe_user_in_db.bio,
            image=maybe_user_in_db.image,
            token=token,
        )
    )


user_path_item = Path("/users/user")
