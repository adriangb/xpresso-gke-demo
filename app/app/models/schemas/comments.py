from typing import List

from pydantic import BaseModel

from app.models.domain.comments import Comment


class ListOfCommentsInResponse(BaseModel):
    comments: List[Comment]


class CommentInResponse(BaseModel):
    comment: Comment


class CommentInCreate(BaseModel):
    body: str
