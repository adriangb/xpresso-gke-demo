from datetime import datetime

from pydantic import BaseModel

from app.models.schemas.configs import ModelInResponseConfig
from app.models.schemas.profiles import Profile


class CommentForResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    body: str
    author: Profile

    Config = ModelInResponseConfig


class CommentInResponse(BaseModel):
    comment: CommentForResponse


class CommentsInResponse(BaseModel):
    comments: list[CommentForResponse]


class CommentForCreate(BaseModel):
    body: str


class CommentInCreate(BaseModel):
    comment: CommentForCreate
