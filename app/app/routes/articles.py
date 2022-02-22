from xpresso import FromQuery

from app.db.repositories.articles import ArticlesRepository
from app.models.conversions import convert_article_in_db_to_article_for_response
from app.models.schemas.articles import ArticlesInResponse
from app.routes.utils import Pagination
from app.services.user import OptionalLoggedInUser, RequireLoggedInUser


async def list_articles(
    articles_repo: ArticlesRepository,
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
        articles=[
            convert_article_in_db_to_article_for_response(article)
            for article in articles
        ]
    )


async def get_user_feed(
    articles_repo: ArticlesRepository,
    pagination: Pagination,
    current_user: RequireLoggedInUser,
) -> ArticlesInResponse:
    articles = await articles_repo.get_articles_by_followed_users(
        current_user_id=current_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return ArticlesInResponse.construct(
        articles=[
            convert_article_in_db_to_article_for_response(article)
            for article in articles
        ]
    )
