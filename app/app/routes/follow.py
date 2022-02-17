from xpresso import FromHeader, FromPath, HTTPException, status

from app.db.repositories.profiles import FolloweeDoesNotExist, ProfilesRepository
from app.models.schemas.profiles import Profile, ProfileInResponse
from app.routes.utils import extract_token_from_authroization_header
from app.services.auth import AuthService


async def follow_user_endpoint(
    username: FromPath[str],
    authorization: FromHeader[str],
    auth_service: AuthService,
    repo: ProfilesRepository,
) -> ProfileInResponse:
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    # make the link
    try:
        followed_profile = await repo.follow_user(
            username_to_follow=username, id_of_current_user=user_id
        )
    except FolloweeDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": f"No user found with username {username}"},
        )
    # build and return the profile
    return ProfileInResponse(
        profile=Profile(
            username=followed_profile.username,
            bio=followed_profile.bio,
            image=followed_profile.image,
            following=True,
        )
    )


async def unfollow_user_endpoint(
    username: FromPath[str],
    authorization: FromHeader[str],
    auth_service: AuthService,
    repo: ProfilesRepository,
) -> ProfileInResponse:
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    # unlink in db
    try:
        followed_profile = await repo.unfollow_user(
            username_to_unfollow=username, id_of_current_user=user_id
        )
    except FolloweeDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": f"No user found with username {username}"},
        )
    # build and return the profile
    return ProfileInResponse(
        profile=Profile(
            username=followed_profile.username,
            bio=followed_profile.bio,
            image=followed_profile.image,
            following=False,
        )
    )
