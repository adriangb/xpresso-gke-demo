from xpresso import FromHeader, FromPath, HTTPException, status

from app.db.repositories.profiles import FolloweeDoesNotExist, ProfilesRepository
from app.models.schemas.profiles import Profile, ProfileInResponse
from app.routes.utils import extract_token_from_authroization_header
from app.services.auth import AuthService


async def get_profile_endpoint(
    username: FromPath[str],
    authorization: FromHeader[str],
    auth_service: AuthService,
    repo: ProfilesRepository,
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
