from xpresso import FromPath, HTTPException, status

from app.db.repositories.exceptions import ResourceDoesNotExistError
from app.db.repositories.profiles import ProfilesRepo
from app.dependencies import OptionalLoggedInUser, RequireLoggedInUser
from app.models.schemas.profiles import Profile, ProfileInResponse


async def get_profile(
    username: FromPath[str],
    current_user: OptionalLoggedInUser | None,
    repo: ProfilesRepo,
) -> ProfileInResponse:
    try:
        profile = await repo.get_profile(
            current_user_id=None if current_user is None else current_user.id,
            username_of_target_profile=username,
        )
    except ResourceDoesNotExistError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": f"No user found with username {username}"},
        ) from exc
    # build and return the profile
    return ProfileInResponse.construct(
        profile=Profile.construct(
            username=profile.username,
            bio=profile.bio,
            image=profile.image,
            following=profile.following,
        )
    )


async def follow_user(
    username: FromPath[str],
    current_user: RequireLoggedInUser,
    repo: ProfilesRepo,
) -> ProfileInResponse:
    try:
        followed_profile = await repo.follow_user(
            current_user_id=current_user.id,
            username_to_follow=username,
        )
    except ResourceDoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": f"No user found with username {username}"},
        )
    return ProfileInResponse.construct(
        profile=Profile.construct(
            username=followed_profile.username,
            bio=followed_profile.bio,
            image=followed_profile.image,
            following=True,
        )
    )


async def unfollow_user(
    username: FromPath[str],
    current_user: RequireLoggedInUser,
    repo: ProfilesRepo,
) -> ProfileInResponse:
    try:
        followed_profile = await repo.unfollow_user(
            current_user_id=current_user.id,
            username_to_unfollow=username,
        )
    except ResourceDoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": f"No user found with username {username}"},
        )
    return ProfileInResponse.construct(
        profile=Profile.construct(
            username=followed_profile.username,
            bio=followed_profile.bio,
            image=followed_profile.image,
            following=True,
        )
    )
