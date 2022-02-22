from typing import Annotated

from pydantic import Field
from xpresso import FromHeader, FromJson, FromQuery, HTTPException, status

from app.db.repositories.articles import ArticlesRepository
from app.db.repositories.users import UsersRepository
from app.models.schemas.articles import Article, ArticleInCreate, ArticleInResponse
from app.models.schemas.auth import Unauthorized
from app.models.schemas.profiles import Profile
from app.routes.utils import extract_token_from_authroization_header
from app.services.auth import AuthService


async def create_article(
    authorization: FromHeader[str],
    article: FromJson[ArticleInCreate],
    auth_service: AuthService,
    users_repo: UsersRepository,
    articles_repo: ArticlesRepository,
) -> ArticleInResponse:
    # verify the author's idenetity
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    maybe_user_in_db = await users_repo.get_user_by_id(id=user_id)
    if maybe_user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Unauthorized.construct(reason="Invalid credentials"),
        )
    # publish the article
    article_info = article.article
    tags = article_info.tags or []
    published_article = await articles_repo.create_article(
        author_id=user_id,
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
                username=maybe_user_in_db.username,
                bio=maybe_user_in_db.bio,
                image=maybe_user_in_db.image,
                following=False,  # by definition
            ),
            created_at=published_article.created_at,
            updated_at=published_article.updated_at,
            favorites_count=0,
            favorited=False,
        )
    )


async def list_articles(
    auth_service: AuthService,
    users_repo: UsersRepository,
    articles_repo: ArticlesRepository,
    # super hacky workaround for https://github.com/samuelcolvin/pydantic/issues/2971
    # otherwise, we'd just use default values instead of poinless lambdas
    limit: Annotated[FromQuery[int], Field(get=0, le=50, default_factory=lambda: 20)],
    offset: Annotated[FromQuery[int], Field(get=0, le=1000, default_factory=lambda: 0)],
    authorization: FromHeader[str | None] = None,
    tag: FromQuery[str | None] = None,
    author: FromQuery[str | None] = None,
    favorited: FromQuery[str | None] = None,
) -> list[ArticleInResponse]:
    # verify the user's identity
    if authorization:
        token = extract_token_from_authroization_header(authorization)
        user_id = auth_service.verify_access_token_and_extract_user_id(token)
        maybe_user_in_db = await users_repo.get_user_by_id(id=user_id)
        if maybe_user_in_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=Unauthorized.construct(reason="Invalid credentials"),
            )
        user_id = maybe_user_in_db.id
    else:
        user_id = None
    # query the db for articles matching the criteria
    articles = await articles_repo.list_articles(
        current_user_id=user_id,
        tag=tag,
        author_username=author,
        favorited_by_username=favorited,
        limit=limit,
        offset=offset,
    )
    # build and return the article
    return [
        ArticleInResponse(
            article=Article(
                slug=str(article.id),
                title=article.title,
                description=article.description,
                body=article.body,
                tags=article.tags,
                author=Profile(
                    username=article.author.username,
                    bio=article.author.bio,
                    image=article.author.image,
                    following=article.author.following,
                ),
                created_at=article.created_at,
                updated_at=article.updated_at,
                favorites_count=article.favorites_count,
                favorited=article.favorited,
            )
        )
        for article in articles
    ]
