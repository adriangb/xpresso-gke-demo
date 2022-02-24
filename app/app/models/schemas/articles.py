from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.models.domain.articles import Article as ArticleDomainModel
from app.models.schemas.configs import ModelInRequestConfig, ModelInResponseConfig
from app.models.schemas.profiles import Profile

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class Article(BaseModel):
    slug: str
    title: str
    description: str
    body: str
    tags: Annotated[list[str], Field(alias="tagList")]
    author: Profile
    favorited: bool
    favorites_count: int
    created_at: datetime
    updated_at: datetime

    Config = ModelInResponseConfig

    @staticmethod
    def from_domain_model(article: ArticleDomainModel) -> "Article":
        return Article.construct(
            slug=str(article.id),
            title=article.title,
            description=article.description,
            body=article.body,
            tags=article.tags,
            author=Profile.construct(
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


class ArticleInResponse(BaseModel):
    article: Article


class ArticlesInResponse(BaseModel):
    articles: list[Article]


class ArticleForCreate(BaseModel):
    title: str
    description: str
    body: str
    tags: list[str] | None = Field(alias="tagList")

    Config = ModelInRequestConfig


class ArticleInCreate(BaseModel):
    article: ArticleForCreate


class ArticleForUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    body: str | None = None


class ArticleInUpdate(BaseModel):
    article: ArticleForUpdate


class ListOfArticlesInResponse(BaseModel):
    articles: list[Article]
    articles_count: int

    Config = ModelInResponseConfig


class ArticlesFilters(BaseModel):
    tag: str | None = None
    author: str | None = None
    favorited: str | None = None
    limit: Annotated[int, Field(ge=1)] = DEFAULT_ARTICLES_LIMIT
    offset: Annotated[int, Field(ge=0)] = DEFAULT_ARTICLES_OFFSET
