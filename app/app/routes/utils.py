from dataclasses import dataclass
from typing import Annotated

from pydantic import Field
from xpresso import FromQuery


@dataclass(slots=True)
class Pagination:
    # super hacky workaround for https://github.com/samuelcolvin/pydantic/issues/2971
    # otherwise, we'd just use default values instead of pointless lambdas
    limit: Annotated[FromQuery[int], Field(get=0, le=50, default_factory=lambda: 20)]
    offset: Annotated[FromQuery[int], Field(get=0, le=1000, default_factory=lambda: 0)]
