from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

from xpresso import FromJson, FromPath, HTTPException, status

from app.db.repositories.articles import CommentNotFound, InjectArticlesRepo
from app.dependencies import OptionalLoggedInUser, RequireLoggedInUser
from app.models.schemas.comments import (
    CommentForResponse,
    CommentInCreate,
    CommentInResponse,
    CommentsInResponse,
)
from app.models.schemas.profiles import Profile


@contextmanager
def handle_comment_not_found(comment_id: UUID) -> Iterator[None]:
    try:
        yield
    except CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Comment "{comment_id}" not found',
        )


async def create_comment(
    current_user: RequireLoggedInUser,
    comment: FromJson[CommentInCreate],
    repo: InjectArticlesRepo,
    slug: FromPath[UUID],
) -> CommentInResponse:
    created_comment = await repo.add_comment_to_article(
        current_user_id=current_user.id,
        article_id=slug,
        body=comment.comment.body,
    )
    return CommentInResponse.construct(
        comment=CommentForResponse.construct(
            id=str(created_comment.id),
            body=comment.comment.body,
            created_at=created_comment.created_at,
            updated_at=created_comment.updated_at,
            author=Profile.construct(
                username=created_comment.author.username,
                bio=created_comment.author.bio,
                image=created_comment.author.image,
                following=created_comment.author.following,
            ),
        )
    )


async def delete_comment(
    current_user: RequireLoggedInUser,
    comment_id: FromPath[UUID],
    repo: InjectArticlesRepo,
    slug: FromPath[UUID],
) -> None:
    try:
        await repo.delete_comment(
            current_user_id=current_user.id,
            comment_id=comment_id,
        )
    except CommentNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Comment "{comment_id}" not found',
        )


async def get_comments_for_article(
    current_user: OptionalLoggedInUser,
    comment: FromJson[CommentInCreate],
    repo: InjectArticlesRepo,
    slug: FromPath[UUID],
) -> CommentsInResponse:
    comments = await repo.get_comments_for_article(
        current_user_id=None if current_user is None else current_user.id,
        article_id=slug,
    )
    return CommentsInResponse(
        comments=[
            CommentForResponse.construct(
                id=str(comment.id),
                body=comment.body,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                author=Profile.construct(
                    username=comment.author.username,
                    bio=comment.author.bio,
                    image=comment.author.image,
                    following=comment.author.following,
                ),
            )
            for comment in comments
        ]
    )
