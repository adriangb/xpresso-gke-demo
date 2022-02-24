from datetime import datetime

from pydantic import BaseModel

from app.models.domain.comments import Comment as CommentDomainModel
from app.models.schemas.configs import ModelInResponseConfig
from app.models.schemas.profiles import Profile


class Comment(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    body: str
    author: Profile

    Config = ModelInResponseConfig

    @staticmethod
    def from_domain_model(comment: CommentDomainModel) -> "Comment":
        return Comment(
            id=str(comment.id),
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            body=comment.body,
            author=Profile.from_domain_model(comment.author),
        )


class CommentInResponse(BaseModel):
    comment: Comment


class CommentsInResponse(BaseModel):
    comments: list[Comment]


class CommentForCreate(BaseModel):
    body: str


class CommentInCreate(BaseModel):
    comment: CommentForCreate
