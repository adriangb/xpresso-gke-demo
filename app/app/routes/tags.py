from app.db.repositories.tags import TagsRepo
from app.models.schemas.tags import TagsInResponse


async def list_tags(repo: TagsRepo) -> TagsInResponse:
    return TagsInResponse.construct(tags=await repo.get_tags())
