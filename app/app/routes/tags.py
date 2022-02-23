from app.db.repositories.tags import InjectTagsRepo
from app.models.schemas.tags import TagsInResponse


async def list_tags(repo: InjectTagsRepo) -> TagsInResponse:
    return TagsInResponse.construct(tags=await repo.get_tags())
