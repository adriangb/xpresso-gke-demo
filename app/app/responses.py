from typing import Any, Awaitable, Callable, Mapping, Optional

from pydantic import BaseModel
from xpresso import Operation
from xpresso.responses import Response

from app.encoder import OrjsonPydanticOutEncoder

encoder = OrjsonPydanticOutEncoder()


def create_json_operation(
    endpoint: Callable[..., Awaitable[BaseModel]],
    status_code: int = 200,
    headers: Optional[Mapping[str, str]] = None,
) -> Operation:
    resp_headers = dict(headers or {})
    resp_headers["Content-Type"] = "application/json"

    def make_response(content: Any) -> Response:
        return Response(content, status_code=status_code, headers=resp_headers)

    return Operation(
        endpoint,
        response_encoder=encoder,
        response_factory=make_response,
    )
