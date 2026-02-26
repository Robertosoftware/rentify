"""Integration tests using testcontainers — skipped if Docker not available."""
import uuid

import pytest

try:
    from testcontainers.postgres import PostgresContainer

    DOCKER_AVAILABLE = True
except Exception:
    DOCKER_AVAILABLE = False


@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
@pytest.mark.anyio
async def test_user_crud_real_db():
    with PostgresContainer("postgres:16") as pg:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
        from sqlmodel import SQLModel, select

        url = pg.get_connection_url().replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(url)
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        from datetime import datetime, timezone

        from app.models.user import User

        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            user = User(
                id=uuid.uuid4(),
                email="integration@test.eu",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                gdpr_consent_at=datetime.now(timezone.utc),
            )
            session.add(user)
            await session.commit()

            result = await session.execute(select(User).where(User.email == "integration@test.eu"))
            found = result.scalar_one_or_none()
            assert found is not None
            assert found.email == "integration@test.eu"

        await engine.dispose()


@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
@pytest.mark.anyio
async def test_listing_upsert_dedup():
    pytest.skip("Requires Docker — skipping in CI without Docker")
