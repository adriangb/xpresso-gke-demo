from pydantic import BaseModel

from app.models.schemas.configs import ModelInResponseConfig


class TagsInList(BaseModel):
    tags: list[str]

    Config = ModelInResponseConfig
