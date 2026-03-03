"""Integration tests against the real Postgres instance in the devcontainer.

These tests use the `postgres` service that is already running as part of the
docker-compose devcontainer stack.  No testcontainers/Docker-in-Docker tricks
are needed — the `postgres` hostname is directly reachable from inside the
devcontainer because both containers share the same Docker Compose network.

Skip when DATABASE_URL_SYNC is not configured or the DB is unreachable.
"""

import os
import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@postgres:5432/rentify",
)

# Quick reachability check at collection time so the test is skipped rather
# than erroring when no DB is available (e.g. plain CI without a Postgres
# service, or running tests on a laptop without docker-compose up).
_DB_AVAILABLE = False
try:
    import socket

    _host = DB_URL.split("@")[-1].split(":")[0]
    _port = int(DB_URL.split("@")[-1].split(":")[1].split("/")[0])
    with socket.create_connection((_host, _port), timeout=2):
        _DB_AVAILABLE = True
except Exception:
    pass


@pytest.mark.skipif(not _DB_AVAILABLE, reason="Postgres not reachable — start docker-compose services first")
@pytest.mark.anyio
async def test_user_crud_real_db():
    """Create and read a user using the real async Postgres driver."""
    from app.models.user import User

    engine = create_async_engine(DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    unique_email = f"integration-{uuid.uuid4().hex[:8]}@test.eu"
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        user = User(
            id=uuid.uuid4(),
            email=unique_email,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            gdpr_consent_at=datetime.now(UTC),
        )
        session.add(user)
        await session.commit()

        result = await session.execute(select(User).where(User.email == unique_email))
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.email == unique_email

        # Clean up — soft-delete so we don't accumulate test rows
        found.deleted_at = datetime.now(UTC)
        await session.commit()

    await engine.dispose()


@pytest.mark.skipif(not _DB_AVAILABLE, reason="Postgres not reachable — start docker-compose services first")
@pytest.mark.anyio
async def test_listing_upsert_dedup():
    """Insert the same listing twice — ON CONFLICT must not create a duplicate."""
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    from app.models.listing import Listing

    engine = create_async_engine(DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    source_id = f"inttest-{uuid.uuid4().hex[:8]}"
    now = datetime.now(UTC)

    async with session_factory() as session:
        listing = Listing(
            id=uuid.uuid4(),
            source_site="test",
            source_id=source_id,
            source_url=f"https://example.com/{source_id}",
            title="Test Listing",
            price_eur=120000,
            price_type="per_month",
            city="amsterdam",
            country_code="NL",
            first_seen_at=now,
            last_seen_at=now,
            created_at=now,
        )
        session.add(listing)
        await session.commit()

        # Second insert — simulate an upsert (update last_seen_at)
        stmt = (
            pg_insert(Listing)
            .values(
                id=uuid.uuid4(),
                source_site="test",
                source_id=source_id,
                source_url=f"https://example.com/{source_id}",
                title="Test Listing Updated",
                price_eur=130000,
                price_type="per_month",
                city="amsterdam",
                country_code="NL",
                first_seen_at=now,
                last_seen_at=now,
                created_at=now,
            )
            .on_conflict_do_update(
                constraint="uq_listing_source",
                set_={"last_seen_at": now, "title": "Test Listing Updated"},
            )
        )
        await session.execute(stmt)
        await session.commit()
        session.expire_all()  # flush SQLAlchemy identity map so the next select re-reads from DB

        result = await session.execute(
            select(Listing).where(Listing.source_site == "test", Listing.source_id == source_id)
        )
        rows = result.scalars().all()
        assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
        assert rows[0].title == "Test Listing Updated"

        # Clean up
        await session.delete(rows[0])
        await session.commit()

    await engine.dispose()
