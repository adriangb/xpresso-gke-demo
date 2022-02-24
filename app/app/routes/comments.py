from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

from xpresso import FromJson, FromPath, HTTPException, status

from app.db.repositories.articles import ArticlesRepo
from app.db.repositories.comments import CommentsRepo
from app.db.repositories.exceptions import ResourceDoesNotExistError
from app.dependencies import OptionalLoggedInUser, RequireLoggedInUser
from app.models.schemas.comments import (
    Comment,
    CommentInCreate,
    CommentInResponse,
    CommentsInResponse,
)


@contextmanager
def _handle_comment_not_found(comment_id: UUID) -> Iterator[None]:
    try:
        yield
    except ResourceDoesNotExistError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Comment "{comment_id}" not found',
        )


async def create_comment(
    current_user: RequireLoggedInUser,
    comment_info: FromJson[CommentInCreate],
    repo: ArticlesRepo,
    slug: FromPath[UUID],
) -> CommentInResponse:
    comment = await repo.add_comment_to_article(
        current_user_id=current_user.id,
        article_id=slug,
        body=comment_info.comment.body,
    )
    return CommentInResponse.construct(comment=Comment.from_domain_model(comment))


async def delete_comment(
    current_user: RequireLoggedInUser,
    comment_id: FromPath[UUID],
    repo: CommentsRepo,
    slug: FromPath[UUID],
) -> None:
    with _handle_comment_not_found(comment_id):
        await repo.delete_comment(
            current_user_id=current_user.id,
            comment_id=comment_id,
        )


async def get_comments_for_article(
    current_user: OptionalLoggedInUser,
    repo: CommentsRepo,
    slug: FromPath[UUID],
) -> CommentsInResponse:
    comments = await repo.get_comments_for_article(
        current_user_id=None if current_user is None else current_user.id,
        article_id=slug,
    )
    return CommentsInResponse(
        comments=[Comment.from_domain_model(comment) for comment in comments]
    )
