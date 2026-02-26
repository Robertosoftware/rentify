"""Create a demo user for development."""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, select

from app.config import get_settings
from app.models import User
from app.services.auth_service import hash_password

settings = get_settings()


async def create_demo_user():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(User).where(User.email == "demo@rentify.eu"))
        existing = result.scalar_one_or_none()
        if existing:
            print("Demo user already exists")
            return

        user = User(
            id=uuid.uuid4(),
            email="demo@rentify.eu",
            hashed_password=hash_password("demo1234"),
            full_name="Demo User",
            subscription_status="trialing",
            gdpr_consent_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.commit()
        print(f"Demo user created: demo@rentify.eu / demo1234 (id={user.id})")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_demo_user())
