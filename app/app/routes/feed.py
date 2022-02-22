from app.db.repositories.articles import ArticlesRepository
from app.models.conversions import convert_article_in_db_to_article_in_response
from app.models.schemas.articles import ArticleInResponse
from app.routes.utils import Pagination
from app.services.user import RequireLoggedInUser


async def get_user_feed(
    articles_repo: ArticlesRepository,
    pagination: Pagination,
    current_user: RequireLoggedInUser,
) -> list[ArticleInResponse]:
    # query the db for articles matching the criteria
    articles = await articles_repo.get_articles_by_followed_users(
        current_user_id=current_user.id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    # build and return the article
    return [
        convert_article_in_db_to_article_in_response(article) for article in articles
    ]
