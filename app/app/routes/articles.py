from uuid import UUID

from xpresso import FromPath, FromQuery, HTTPException, status

from app.db.repositories.articles import ArticleNotFound, ArticlesRepository
from app.models.conversions import convert_article_in_db_to_article_in_response
from app.models.schemas.articles import Article, ArticleInCreate, ArticleInResponse
from app.models.schemas.profiles import Profile
from app.requests import OrJSON
from app.routes.utils import Pagination
from app.services.user import OptionalLoggedInUser, RequireLoggedInUser


async def create_article(
    current_user: RequireLoggedInUser,
    article: OrJSON[ArticleInCreate],
    articles_repo: ArticlesRepository,
) -> ArticleInResponse:
    # verify the author's idenetity
    # publish the article
    article_info = article.article
    tags = article_info.tags or []
    published_article = await articles_repo.create_article(
        author_id=current_user.id,
        title=article_info.title,
        body=article_info.body,
        description=article_info.description,
        tags=article_info.tags,
    )
    # build and return the article
    return ArticleInResponse(
        article=Article(
            slug=str(published_article.id),
            title=article_info.title,
            description=article_info.description,
            body=article_info.body,
            tags=tags,
            author=Profile(
                username=current_user.username,
                bio=current_user.bio,
                image=current_user.image,
                following=False,  # by definition
            ),
            created_at=published_article.created_at,
            updated_at=published_article.updated_at,
            favorites_count=0,
            favorited=False,
        )
    )


async def list_articles(
    articles_repo: ArticlesRepository,
    pagination: Pagination,
    current_user: OptionalLoggedInUser = None,
    tag: FromQuery[str | None] = None,
    author: FromQuery[str | None] = None,
    favorited: FromQuery[str | None] = None,
) -> list[ArticleInResponse]:
    user_id = current_user.id if current_user is not None else None
    # query the db for articles matching the criteria
    articles = await articles_repo.list_articles(
        current_user_id=user_id,
        tag=tag,
        author_username=author,
        favorited_by_username=favorited,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    # build and return the article
    return [
        convert_article_in_db_to_article_in_response(article) for article in articles
    ]


async def delete_article(
    articles_repo: ArticlesRepository,
    current_user: RequireLoggedInUser,
    slug: FromPath[str],
) -> None:
    # keep the fact that the slug is a UUID an implementation detail
    try:
        article_id = UUID(slug)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Article {slug} not found"
        ) from exc
    # query the db for articles matching the criteria
    try:
        await articles_repo.delete_article(
            article_id=article_id, current_user_id=current_user.id
        )
    except ArticleNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Article {slug} not found"
        )
