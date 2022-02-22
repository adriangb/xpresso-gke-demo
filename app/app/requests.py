from typing import Annotated, TypeVar

from orjson import loads
from xpresso import Json

T = TypeVar("T")


OrJSON = Annotated[T, Json(decoder=loads)]  # type: ignore[arg-type]  # orjson has kw only args
