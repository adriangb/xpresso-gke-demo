from xpresso import FromHeader, FromPath, HTTPException, Path, status

from app.db.repositories.profiles import FollowedUserDoesNotExist, ProfilesRepository
from app.models.domain.profiles import Profile
from app.models.schemas.profiles import ProfileInResponse
from app.routes.utils import extract_token_from_authroization_header
from app.services.auth import AuthService


async def follow_user(
    username: FromPath[str],
    authorization: FromHeader[str],
    auth_service: AuthService,
    profiles_repo: ProfilesRepository,
) -> ProfileInResponse:
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    # make the link
    try:
        followed_profile = await profiles_repo.follow_user(
            username_to_follow=username, user_id=user_id
        )
    except FollowedUserDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": f"User {username} does not exist"},
        )
    # TODO: handle case where the user the token belongs to does not exist
    # build and return the profile
    return ProfileInResponse(
        profile=Profile(
            username=followed_profile.username,
            bio=followed_profile.bio,
            image=followed_profile.image,
            following=True,
        )
    )


path_item = Path("/profiles/{username}/follow", post=follow_user)
