from argon2.exceptions import VerificationError
from xpresso import FromJson, HTTPException, Path, status

from app.db.repositories.users import UsersRepository
from app.dependencies import PasswordHasher
from app.models.schemas.users import UserInLogin, UserInResponse, UserWithToken
from app.services.auth import AuthService


async def login(
    user: FromJson[UserInLogin],
    auth_service: AuthService,
    repo: UsersRepository,
    hasher: PasswordHasher,
) -> UserInResponse:
    user_info = user.user
    # check that the user exists in the database
    maybe_user_in_db = await repo.get_user_by_email(email=user_info.email)
    if maybe_user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"reason": "Invalid credentials"},
        )
    # check that the password matches
    try:
        hasher.verify(maybe_user_in_db.hashed_password, user_info.password)
    except VerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"reason": "Invalid credentials"},
        ) from e
    # rehash the password if needed
    if hasher.check_needs_rehash(maybe_user_in_db.hashed_password):
        hashed_password = hasher.hash(user_info.password)
        await repo.update_user(
            user_id=maybe_user_in_db.id, hashed_password=hashed_password
        )
    # create a jwt token
    token = auth_service.create_access_token(user_id=maybe_user_in_db.id)
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


path_item = Path("/users/login", post=login)
