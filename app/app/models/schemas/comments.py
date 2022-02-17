from datetime import datetime
from pydantic import BaseModel

from app.models.schemas.profiles import Profile, ProfileInResponse
from app.models.schemas.configs import ModelInResponseConfig


class Comment(BaseModel):
    body: str
    author: Profile


class CommentForResponse(Comment):
    created_at: datetime
    updated_at: datetime

    Config = ModelInResponseConfig


class CommentInResponse(BaseModel):
    comment: CommentForResponse


class ListOfCommentsInResponse(BaseModel):
    comments: list[CommentForResponse]


class CommentInCreate(BaseModel):
    body: str
