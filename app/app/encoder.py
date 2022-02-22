from orjson import dumps
from pydantic import BaseModel
from xpresso.encoders.api import Encoder


class OrjsonPydanticOutEncoder(Encoder):
    def __call__(self, obj: BaseModel | list[BaseModel]) -> bytes:
        if isinstance(obj, list):
            return dumps([o.dict(by_alias=True) for o in obj])
        return dumps(obj.dict(by_alias=True))


class IdentityEncoder(Encoder):
    def __call__(self, obj: None) -> bytes:
        return b""
