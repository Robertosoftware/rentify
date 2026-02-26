import json
import uuid

import pytest


@pytest.mark.anyio
async def test_create_checkout_session_mock(async_client, test_user, auth_headers):
    response = await async_client.post("/billing/create-checkout-session", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "url" in data


@pytest.mark.anyio
async def test_webhook_valid_signature(async_client):
    payload = json.dumps({
        "id": f"evt_{uuid.uuid4().hex}",
        "type": "checkout.session.completed",
        "data": {"object": {"customer": "cus_test"}},
    })
    response = await async_client.post(
        "/stripe/webhook",
        content=payload,
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_webhook_idempotency(async_client):
    event_id = f"evt_{uuid.uuid4().hex}"
    payload = json.dumps({
        "id": event_id,
        "type": "checkout.session.completed",
        "data": {"object": {"customer": "cus_idempotent"}},
    })
    r1 = await async_client.post("/stripe/webhook", content=payload, headers={"content-type": "application/json"})
    r2 = await async_client.post("/stripe/webhook", content=payload, headers={"content-type": "application/json"})
    assert r1.status_code == 200
    assert r2.status_code == 200
