import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import get_settings
from app.models.feature_flag import FeatureFlag

settings = get_settings()
log = structlog.get_logger()


async def get_flag(name: str, db: AsyncSession) -> bool:
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.name == name))
    flag = result.scalar_one_or_none()
    if flag is None:
        # Fall back to env defaults
        defaults = {
            "paid_gate_enabled": settings.ENABLE_PAID_GATE,
            "scraping_enabled": settings.ENABLE_SCRAPING,
            "telegram_notifications_enabled": False,
            "email_notifications_enabled": False,
        }
        return defaults.get(name, False)
    return flag.enabled
