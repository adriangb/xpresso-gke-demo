from xpresso import FromQuery

from app.db.repositories.articles import ArticlesRepo
from app.dependencies import OptionalLoggedInUser
from app.models.schemas.articles import Article, ArticlesInResponse
from app.routes.utils import Pagination


async def list_articles(
    articles_repo: ArticlesRepo,
    pagination: Pagination,
    current_user: OptionalLoggedInUser = None,
    tag: FromQuery[str | None] = None,
    author: FromQuery[str | None] = None,
    favorited: FromQuery[str | None] = None,
) -> ArticlesInResponse:
    articles = await articles_repo.list_articles(
        current_user_id=current_user.id if current_user is not None else None,
        tag=tag,
        author_username=author,
        favorited_by_username=favorited,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return ArticlesInResponse.construct(
        articles=[Article.from_domain_model(article) for article in articles]
    )
