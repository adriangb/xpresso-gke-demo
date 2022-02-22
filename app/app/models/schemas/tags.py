from pydantic import BaseModel


class TagsInResponse(BaseModel):
    tags: list[str]
