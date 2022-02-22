from app.db.repositories.articles import ArticleInDB
from app.models.schemas.articles import Article, ArticleInResponse
from app.models.schemas.profiles import Profile


def convert_article_in_db_to_article_for_response(article: ArticleInDB) -> Article:
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


def convert_article_in_db_to_article_in_response(
    article: ArticleInDB,
) -> ArticleInResponse:
    return ArticleInResponse.construct(
        article=convert_article_in_db_to_article_for_response(article)
    )
