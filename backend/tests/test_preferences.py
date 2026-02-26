import pytest


@pytest.mark.anyio
async def test_create_preference(async_client, test_user, auth_headers):
    response = await async_client.post(
        "/preferences",
        headers=auth_headers,
        json={"city": "amsterdam", "max_price": 200000, "country_code": "NL"},
    )
    assert response.status_code == 201
    assert response.json()["city"] == "amsterdam"


@pytest.mark.anyio
async def test_list_preferences(async_client, test_user, auth_headers):
    response = await async_client.get("/preferences", headers=auth_headers)
    assert response.status_code == 200
    assert "items" in response.json()


@pytest.mark.anyio
async def test_preference_limit_free_user(async_client, test_user, auth_headers):
    for i in range(3):
        r = await async_client.post(
            "/preferences",
            headers=auth_headers,
            json={"city": f"city{i}", "max_price": 150000 + i * 10000},
        )
        assert r.status_code == 201

    r = await async_client.post(
        "/preferences",
        headers=auth_headers,
        json={"city": "extra_city", "max_price": 200000},
    )
    assert r.status_code == 403
