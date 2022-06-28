from contextlib import AsyncExitStack
from typing import Annotated, AsyncIterator

from httpx import AsyncClient
from xpresso import App, Depends, FromQuery, Path
from xpresso.responses import StreamingResponse, ResponseSpec


def list_primes(n: int) -> list[int]:
    # https://stackoverflow.com/questions/2068372
    """Returns  a list of primes < n"""
    if n < 2:
        return []
    sieve = [True] * n
    for i in range(3, int(n**0.5) + 1, 2):
        if sieve[i]:
            sieve[i * i :: 2 * i] = [False] * int(((n - i * i - 1) / (2 * i) + 1))
    return [2] + [i for i in range(3, n, 2) if sieve[i]]


async def filter_primes(
    n: FromQuery[int],
) -> list[int]:
    return list_primes(n)


async def get_stack() -> AsyncIterator[AsyncExitStack]:
    async with AsyncExitStack() as stack:
        yield stack


async def get_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient() as client:
        yield client


HTTPClient = Annotated[AsyncClient, Depends(get_client, scope="app")]
Stack = Annotated[AsyncExitStack, Depends(get_stack, scope="connection")]


async def proxy_image(
    client: HTTPClient,
    stack: Stack,
) -> StreamingResponse:
    # do some IO
    resp = await stack.enter_async_context(
        client.stream(  # type: ignore
            "GET",
            "https://raw.githubusercontent.com/adriangb/xpresso/main/docs/assets/images/xpresso-title.png",
        )
    )
    return StreamingResponse(resp.aiter_bytes(), media_type="image/png")


app = App(
    routes=[
        Path("/primes", get=filter_primes),
        Path(
            "/image",
            get=proxy_image,
            responses={200: ResponseSpec(content={"image/png": bytes})},
        ),
    ],
)
