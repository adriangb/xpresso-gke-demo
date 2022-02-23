from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

from xpresso import FromJson, FromPath, HTTPException, status

from app.db.repositories.articles import ArticleNotFound, InjectArticlesRepo
from app.dependencies import OptionalLoggedInUser, RequireLoggedInUser
from app.models.conversions import convert_article_in_db_to_article_in_response
from app.models.schemas.articles import (
    Article,
    ArticleInCreate,
    ArticleInResponse,
    ArticleInUpdate,
)
from app.models.schemas.profiles import Profile


@contextmanager
def handle_article_not_found(slug: UUID) -> Iterator[None]:
    try:
        yield
    except ArticleNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Article "{slug}" not found'
        )


async def create_article(
    current_user: RequireLoggedInUser,
    article: FromJson[ArticleInCreate],
    articles_repo: InjectArticlesRepo,
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


async def delete_article(
    articles_repo: InjectArticlesRepo,
    current_user: RequireLoggedInUser,
    slug: FromPath[UUID],
) -> None:
    with handle_article_not_found(slug):
        await articles_repo.delete_article(
            article_id=slug,
            current_user_id=current_user.id,
        )


async def update_article(
    articles_repo: InjectArticlesRepo,
    current_user: RequireLoggedInUser,
    slug: FromPath[UUID],
    article_info: FromJson[ArticleInUpdate],
) -> ArticleInResponse:
    with handle_article_not_found(slug):
        article = await articles_repo.update_article(
            article_id=slug,
            current_user_id=current_user.id,
            title=article_info.article.title,
            description=article_info.article.description,
            body=article_info.article.body,
        )
    return convert_article_in_db_to_article_in_response(article)


async def get_article(
    articles_repo: InjectArticlesRepo,
    slug: FromPath[UUID],
    current_user: OptionalLoggedInUser = None,
) -> ArticleInResponse:
    with handle_article_not_found(slug):
        article = await articles_repo.get_article_by_id(
            current_user_id=current_user.id if current_user is not None else None,
            article_id=slug,
        )
    return convert_article_in_db_to_article_in_response(article)


async def favorite_article(
    articles_repo: InjectArticlesRepo,
    slug: FromPath[UUID],
    current_user: RequireLoggedInUser,
) -> ArticleInResponse:
    with handle_article_not_found(slug):
        article = await articles_repo.favorite_article(
            current_user_id=current_user.id,
            article_id=slug,
        )
    return convert_article_in_db_to_article_in_response(article)


async def unfavorite_article(
    articles_repo: InjectArticlesRepo,
    slug: FromPath[UUID],
    current_user: RequireLoggedInUser,
) -> ArticleInResponse:
    with handle_article_not_found(slug):
        article = await articles_repo.unfavorite_article(
            current_user_id=current_user.id,
            article_id=slug,
        )
    return convert_article_in_db_to_article_in_response(article)
