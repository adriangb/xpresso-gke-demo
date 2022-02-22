from typing import Any

from orjson import dumps
from pydantic import BaseModel
from xpresso.encoders.api import Encoder


class OrjsonPydanticOutEncoder(Encoder):
    def __call__(self, obj: Any) -> bytes:
        if not isinstance(obj, BaseModel):
            raise TypeError("This encoder only works with Pydantic models")
        return dumps(obj.dict(by_alias=True))
