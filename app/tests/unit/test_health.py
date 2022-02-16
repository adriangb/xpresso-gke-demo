from xpresso import App
from xpresso.testclient import TestClient

from app.db.connection import ConnectionHealth


def test_health(test_app: App) -> None:
    class FakeHealth(ConnectionHealth):
        def __init__(self) -> None:
            pass

        async def is_connected(self) -> bool:
            return True

    with test_app.dependency_overrides as overrides:
        overrides[ConnectionHealth] = FakeHealth

        with TestClient(test_app) as client:
            resp = client.get("/health")
            assert resp.status_code == 200, resp.content
        assert resp.json() == {"db": {"connected": True}}
