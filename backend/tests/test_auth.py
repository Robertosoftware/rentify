import pytest


@pytest.mark.anyio
async def test_register_success(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"email": "new@rentify.eu", "password": "securepass123", "gdpr_consent": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["email"] == "new@rentify.eu"


@pytest.mark.anyio
async def test_register_duplicate_email(async_client, test_user):
    response = await async_client.post(
        "/auth/register",
        json={"email": test_user.email, "password": "securepass123", "gdpr_consent": True},
    )
    assert response.status_code == 409


@pytest.mark.anyio
async def test_register_missing_gdpr_consent(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"email": "nogdpr@rentify.eu", "password": "securepass123", "gdpr_consent": False},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_register_weak_password(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"email": "weak@rentify.eu", "password": "abc", "gdpr_consent": True},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_login_success(async_client, test_user, test_user_data):
    response = await async_client.post(
        "/auth/login",
        json={"email": test_user.email, "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_login_wrong_password(async_client, test_user):
    response = await async_client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_me_authenticated(async_client, test_user, auth_headers):
    response = await async_client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email


@pytest.mark.anyio
async def test_me_unauthenticated(async_client):
    response = await async_client.get("/auth/me")
    assert response.status_code == 401  # no credentials → 401 from HTTPBearer
