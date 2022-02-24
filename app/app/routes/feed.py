from app.db.repositories.feed import FeedRepo
from app.dependencies import RequireLoggedInUser
from app.models.schemas.articles import Article, ArticlesInResponse
from app.routes.utils import Pagination


async def get_user_feed(
    repo: FeedRepo,
    pagination: Pagination,
    current_user: RequireLoggedInUser,
) -> ArticlesInResponse:
    articles = await repo.get_feed(
        current_user_id=current_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return ArticlesInResponse.construct(
        articles=[Article.from_domain_model(article) for article in articles]
    )
