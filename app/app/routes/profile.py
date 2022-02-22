from xpresso import FromPath, HTTPException, status

from app.db.repositories.users import FolloweeDoesNotExist, UsersRepository
from app.models.schemas.profiles import Profile, ProfileInResponse
from app.services.user import RequireLoggedInUser


async def get_profile(
    username: FromPath[str],
    current_user: RequireLoggedInUser,
    repo: UsersRepository,
) -> ProfileInResponse:
    try:
        profile = await repo.get_profile(
            username_of_target_profile=username, id_of_current_user=current_user.id
        )
    except FolloweeDoesNotExist as exc:
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
            following=profile.follows,
        )
    )
