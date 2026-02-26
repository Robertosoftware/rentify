import uuid
from datetime import datetime, timezone

import pytest

from app.models.feature_flag import FeatureFlag
from app.models.listing import Listing


async def _seed_flag(db_session, name, enabled):
    from sqlmodel import select
    result = await db_session.execute(select(FeatureFlag).where(FeatureFlag.name == name))
    flag = result.scalar_one_or_none()
    if flag:
        flag.enabled = enabled
    else:
        flag = FeatureFlag(
            id=uuid.uuid4(),
            name=name,
            enabled=enabled,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(flag)
    await db_session.commit()


async def _seed_listing(db_session):
    listing = Listing(
        id=uuid.uuid4(),
        source_site="test",
        source_id="gate_test_1",
        source_url="https://example.com/1",
        title="Test Apartment",
        price_eur=150000,
        city="amsterdam",
        first_seen_at=datetime.now(timezone.utc),
        last_seen_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(listing)
    await db_session.commit()
    return listing


@pytest.mark.anyio
async def test_paid_gate_disabled_allows_all(async_client, test_user, auth_headers, db_session):
    await _seed_flag(db_session, "paid_gate_enabled", False)
    response = await async_client.get("/listings", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_paid_gate_enabled_blocks_free(async_client, test_user, auth_headers, db_session):
    await _seed_flag(db_session, "paid_gate_enabled", True)
    response = await async_client.get("/listings", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.anyio
async def test_paid_gate_enabled_allows_active(async_client, test_user, auth_headers, db_session):
    await _seed_flag(db_session, "paid_gate_enabled", True)
    test_user.subscription_status = "active"
    await db_session.commit()
    response = await async_client.get("/listings", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_paid_gate_enabled_allows_trialing(async_client, test_user, auth_headers, db_session):
    await _seed_flag(db_session, "paid_gate_enabled", True)
    test_user.subscription_status = "trialing"
    await db_session.commit()
    response = await async_client.get("/listings", headers=auth_headers)
    assert response.status_code == 200
