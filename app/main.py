from typing import Annotated, AsyncIterator

from httpx import AsyncClient
from xpresso import App, Depends, FromQuery, Path


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


async def get_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient() as client:
        yield client


HTTPClient = Annotated[AsyncClient, Depends(get_client, scope="app")]


async def filter_primes(
    n: FromQuery[int],
    client: HTTPClient,
) -> list[int]:
    # do some IO
    data = b"data " * 100
    resp = await client.post(  # type: ignore
        "https://httpbin.org/post",
        content=data,
    )
    resp.raise_for_status()
    # burn some rubber
    return list_primes(n)


app = App(
    routes=[Path("/primes", get=filter_primes)],
)
