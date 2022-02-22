from xpresso import FromPath, HTTPException, status

from app.db.repositories.users import FolloweeDoesNotExist, UsersRepository
from app.models.schemas.profiles import Profile, ProfileInResponse
from app.services.user import RequireLoggedInUser


async def follow_user(
    username: FromPath[str],
    current_user: RequireLoggedInUser,
    repo: UsersRepository,
) -> ProfileInResponse:
    # make the link
    try:
        followed_profile = await repo.follow_user(
            username_to_follow=username, id_of_current_user=current_user.id
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


async def unfollow_user(
    username: FromPath[str],
    current_user: RequireLoggedInUser,
    repo: UsersRepository,
) -> ProfileInResponse:
    # unlink in db
    try:
        followed_profile = await repo.unfollow_user(
            username_to_unfollow=username,
            id_of_current_user=current_user.id,
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
