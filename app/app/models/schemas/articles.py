from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

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


class ArticleInResponse(BaseModel):
    article: Article


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
