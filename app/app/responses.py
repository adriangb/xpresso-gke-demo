from typing import Any, Callable, Mapping, Optional, TypedDict, TypeVar

from pydantic import BaseModel
from xpresso import status
from xpresso.encoders.api import Encoder
from xpresso.responses import Response

from app.encoder import IdentityEncoder, OrjsonPydanticOutEncoder

json_encoder = OrjsonPydanticOutEncoder()
ident_encoder = IdentityEncoder()

Model = TypeVar("Model", bound=BaseModel, covariant=True)


class ResponseParams(TypedDict):
    response_encoder: Encoder
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
        response_encoder=json_encoder,
        response_factory=make_response,
    )


def empty_response(headers: Optional[Mapping[str, str]] = None) -> ResponseParams:
    resp_headers = dict(headers or {})

    def make_response(content: Any) -> Response:
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=resp_headers)

    return ResponseParams(
        response_encoder=ident_encoder,
        response_factory=make_response,
    )
