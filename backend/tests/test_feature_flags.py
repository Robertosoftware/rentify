import uuid
from datetime import datetime, timezone

import pytest

from app.models.feature_flag import FeatureFlag


async def _seed_flag(db_session, name="paid_gate_enabled", enabled=False):
    flag = FeatureFlag(
        id=uuid.uuid4(),
        name=name,
        enabled=enabled,
        description="Test flag",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(flag)
    await db_session.commit()
    return flag


@pytest.mark.anyio
async def test_list_flags(async_client, admin_user, admin_headers, db_session):
    await _seed_flag(db_session)
    response = await async_client.get("/admin/feature-flags", headers=admin_headers)
    assert response.status_code == 200
    assert "items" in response.json()


@pytest.mark.anyio
async def test_update_flag(async_client, admin_user, admin_headers, db_session):
    await _seed_flag(db_session, name="paid_gate_enabled", enabled=False)
    response = await async_client.put(
        "/admin/feature-flags/paid_gate_enabled",
        headers=admin_headers,
        json={"enabled": True},
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is True


@pytest.mark.anyio
async def test_non_admin_rejected(async_client, test_user, auth_headers):
    response = await async_client.get("/admin/feature-flags", headers=auth_headers)
    assert response.status_code == 403
