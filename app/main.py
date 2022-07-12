from contextlib import AsyncExitStack
from typing import Annotated, AsyncIterator

from httpx import AsyncClient
from xpresso import App, Depends, FromQuery, Path
from xpresso.responses import StreamingResponse, ResponseSpec

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


def generate_primes_up_to(n: int) -> list[int]:
    """Returns  a list of primes < n

    This is _extremely_ inefficient but the goal here
    is to burn CPU while not using much memory, so it is
    exactly what we want.
    """
    return [i for i in range(n) if is_prime(i)]


async def filter_primes(
    n: FromQuery[int],
) -> list[int]:
    """An extremely inefficient method to find prime numbers.

    The goal of this endpoint is to simulate CPU bound work.
    """
    return [i for i in range(n) if is_prime(i)]


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
    """An endpoint that simply proxies an image.

    The goal of this endpoint is to simulate IO bound work.
    """
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
