from typing import AsyncGenerator

import asgi_lifespan
import httpx
import pytest
from xpresso import App


@pytest.fixture
async def test_client(test_app: App) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with asgi_lifespan.LifespanManager(test_app):
        async with httpx.AsyncClient(
            app=test_app, base_url="http://example.com"
        ) as client:
            yield client
