from app.db.repositories.tags import TagsRepository
from app.models.schemas.tags import TagsInResponse


async def list_tags(repo: TagsRepository) -> TagsInResponse:
    return TagsInResponse.construct(tags=await repo.get_tags())
