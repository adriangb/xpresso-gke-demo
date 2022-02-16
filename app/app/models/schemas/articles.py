from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.domain.articles import Article

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class ArticleForResponse(Article):
    tags: List[str] = Field(..., alias="tagList")


class ArticleInResponse(BaseModel):
    article: ArticleForResponse


class ArticleInCreate(BaseModel):
    title: str
    description: str
    body: str
    tags: List[str] = Field([], alias="tagList")


class ArticleInUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None


class ListOfArticlesInResponse(BaseModel):
    articles: List[ArticleForResponse]
    articles_count: int


class ArticlesFilters(BaseModel):
    tag: Optional[str] = None
    author: Optional[str] = None
    favorited: Optional[str] = None
    limit: int = Field(DEFAULT_ARTICLES_LIMIT, ge=1)
    offset: int = Field(DEFAULT_ARTICLES_OFFSET, ge=0)
