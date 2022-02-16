from typing import List

from app.models.domain.comments import Comment
from pydantic import BaseModel


class ListOfCommentsInResponse(BaseModel):
    comments: List[Comment]


class CommentInResponse(BaseModel):
    comment: Comment


class CommentInCreate(BaseModel):
    body: str
