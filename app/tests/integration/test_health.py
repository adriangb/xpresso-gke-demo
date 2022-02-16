from httpx import AsyncClient, Response


async def test_healthcheck(test_client: AsyncClient) -> None:
    resp: Response = await test_client.get("/health")
    assert resp.status_code == 200, resp.content
    assert resp.json() == {"db": {"connected": True}}
