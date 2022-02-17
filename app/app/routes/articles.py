from xpresso import FromHeader, FromJson, FromQuery, HTTPException, status

from app.db.repositories.users import UsersRepository
from app.db.repositories.articles import ArticlesRepository
from app.db.repositories.tags import TagsRepository
from app.models.schemas.auth import Unauthorized
from app.routes.utils import extract_token_from_authroization_header
from app.services.auth import AuthService
from app.models.schemas.profiles import Profile
from app.models.schemas.articles import ArticleInCreate, ArticleInResponse, Article


async def create_article_endpoint(
    authorization: FromQuery[str],
    article: FromJson[ArticleInCreate],
    auth_service: AuthService,
    users_repo: UsersRepository,
    articles_repo: ArticlesRepository,
    tags_repositoy: TagsRepository,
) -> ArticleInResponse:
    article_info = article.article
    token = extract_token_from_authroization_header(authorization)
    user_id = auth_service.verify_access_token_and_extract_user_id(token)
    # check that the user exists in the database
    maybe_user_in_db = await users_repo.get_user_by_id(id=user_id)
    if maybe_user_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Unauthorized.construct(reason="Invalid credentials"),
        )
    tags = article_info.tags or []
    # create the tags
    if article.article.tags:
        await tags_repositoy.ensure_tags_exist(tags)
    # publish the article
    published_article = await articles_repo.create_article(
        author_id=user_id,
        title=article_info.title,
        body=article_info.body,
        description=article_info.description,
        tags=article_info.tags,
    )
    # build and return the user model
    return ArticleInResponse(
        article=Article(
            slug=str(published_article.id),
            title=published_article.title,
            description=published_article.description,
            body=published_article.body,
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
