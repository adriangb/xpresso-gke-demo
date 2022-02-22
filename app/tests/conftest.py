from typing import Any, Generator, Type, TypeVar
from unittest.mock import patch

import pytest
from pydantic import BaseModel

Model = TypeVar("Model", bound=BaseModel)


@pytest.fixture(scope="session", autouse=True)
def force_pydantic_validation() -> Generator[None, None, None]:
    """Replace BaseModel.construct with BaseModel.validate to catch
    bugs in tests but keep the overhead low in production.
    """

    def validate(cls: Type[Model], **data: Any) -> Model:
        return cls(**data)

    with patch.object(BaseModel, "construct", new=classmethod(validate)):
        yield
