from httpx import AsyncClient, Response


async def test_registration(test_client: AsyncClient) -> None:
    payload = {
        "user": {"username": "Jacob", "email": "jake@jake.jake", "password": "jakejake"}
    }
    expected_response = {
        "user": {
            "username": "Jacob",
            "email": "jake@jake.jake",
            "bio": None,
            "image": None,
        }
    }
    resp: Response = await test_client.post("/api/users", json=payload)
    assert resp.status_code == 201, resp.content
    resp_data = resp.json()
    resp_data["user"].pop("token")
    assert resp_data == expected_response
