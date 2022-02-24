from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

from xpresso import FromJson, FromPath, HTTPException, status

from app.db.repositories.articles import ArticlesRepo
from app.db.repositories.exceptions import ResourceDoesNotExistError
from app.dependencies import OptionalLoggedInUser, RequireLoggedInUser
from app.models.schemas.articles import (
    Article,
    ArticleInCreate,
    ArticleInResponse,
    ArticleInUpdate,
)


@contextmanager
def _handle_article_not_found(slug: UUID) -> Iterator[None]:
    try:
        yield
    except ResourceDoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'Article "{slug}" not found'
        )


async def create_article(
    current_user: RequireLoggedInUser,
    article: FromJson[ArticleInCreate],
    articles_repo: ArticlesRepo,
) -> ArticleInResponse:
    article_info = article.article
    published_article = await articles_repo.create_article(
        author_id=current_user.id,
        title=article_info.title,
        body=article_info.body,
        description=article_info.description,
        tags=article_info.tags,
    )
    return ArticleInResponse.construct(
        article=Article.from_domain_model(published_article)
    )


async def delete_article(
    articles_repo: ArticlesRepo,
    current_user: RequireLoggedInUser,
    slug: FromPath[UUID],
) -> None:
    with _handle_article_not_found(slug):
        await articles_repo.delete_article(
            article_id=slug,
            current_user_id=current_user.id,
        )


async def update_article(
    articles_repo: ArticlesRepo,
    current_user: RequireLoggedInUser,
    slug: FromPath[UUID],
    article: FromJson[ArticleInUpdate],
) -> ArticleInResponse:
    article_info = article.article
    with _handle_article_not_found(slug):
        updated_article = await articles_repo.update_article(
            article_id=slug,
            current_user_id=current_user.id,
            title=article_info.title,
            description=article_info.description,
            body=article_info.body,
        )
    return ArticleInResponse.construct(
        article=Article.from_domain_model(updated_article)
    )


async def get_article(
    articles_repo: ArticlesRepo,
    slug: FromPath[UUID],
    current_user: OptionalLoggedInUser = None,
) -> ArticleInResponse:
    with _handle_article_not_found(slug):
        article = await articles_repo.get_article_by_id(
            current_user_id=current_user.id if current_user is not None else None,
            article_id=slug,
        )
    return ArticleInResponse.construct(article=Article.from_domain_model(article))


async def favorite_article(
    articles_repo: ArticlesRepo,
    slug: FromPath[UUID],
    current_user: RequireLoggedInUser,
) -> ArticleInResponse:
    with _handle_article_not_found(slug):
        article = await articles_repo.favorite_article(
            current_user_id=current_user.id,
            article_id=slug,
        )
    return ArticleInResponse.construct(article=Article.from_domain_model(article))


async def unfavorite_article(
    articles_repo: ArticlesRepo,
    slug: FromPath[UUID],
    current_user: RequireLoggedInUser,
) -> ArticleInResponse:
    with _handle_article_not_found(slug):
        article = await articles_repo.unfavorite_article(
            current_user_id=current_user.id,
            article_id=slug,
        )
    return ArticleInResponse.construct(article=Article.from_domain_model(article))
