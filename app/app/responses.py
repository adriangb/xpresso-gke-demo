from typing import Any, Callable, Mapping, Optional, TypedDict, TypeVar

from pydantic import BaseModel
from xpresso.responses import Response

from app.encoder import OrjsonPydanticOutEncoder

encoder = OrjsonPydanticOutEncoder()


Model = TypeVar("Model", bound=BaseModel, covariant=True)


class ResponseParams(TypedDict):
    response_encoder: OrjsonPydanticOutEncoder
    response_factory: Callable[[Any], Response]


def orjson_response(
    status_code: int = 200,
    headers: Optional[Mapping[str, str]] = None,
) -> ResponseParams:
    resp_headers = dict(headers or {})
    resp_headers["Content-Type"] = "application/json"

    def make_response(content: Any) -> Response:
        return Response(content, status_code=status_code, headers=resp_headers)

    return ResponseParams(
        response_encoder=encoder,
        response_factory=make_response,
    )
