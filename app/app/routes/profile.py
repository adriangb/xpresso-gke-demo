from xpresso import FromHeader, FromPath, HTTPException, status

from app.db.repositories.followers import FolloweeDoesNotExist, FollowersRepository
from app.models.domain.profiles import Profile
from app.models.schemas.profiles import ProfileInResponse
from app.routes.utils import extract_token_from_authroization_header
from app.services.auth import AuthService


async def get_profile_endpoint(
    username: FromPath[str],
    authorization: FromHeader[str],
    auth_service: AuthService,
    repo: FollowersRepository,
) -> ProfileInResponse:
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    try:
        profile = await repo.get_profile(
            username_of_target_profile=username, id_of_current_user=user_id
        )
    except FolloweeDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": f"No user found with username {username}"},
        )
    # build and return the profile
    return ProfileInResponse(
        profile=Profile(
            username=profile.username,
            bio=profile.bio,
            image=profile.image,
            following=profile.follows,
        )
    )
