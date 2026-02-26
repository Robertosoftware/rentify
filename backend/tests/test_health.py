import pytest


@pytest.mark.anyio
async def test_health_returns_ok(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
