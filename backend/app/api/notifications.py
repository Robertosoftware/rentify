import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()
log = structlog.get_logger()


class TelegramConnect(BaseModel):
    chat_id: str


class NotificationSettings(BaseModel):
    telegram: bool
    email: bool


@router.post("/notifications/telegram/connect")
async def connect_telegram(
    body: TelegramConnect, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict:
    from datetime import datetime, timezone

    current_user.telegram_chat_id = body.chat_id
    current_user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    log.info("telegram.connected", user_id=str(current_user.id), chat_id=body.chat_id)
    return {"status": "connected"}


@router.get("/notifications/settings")
async def get_notification_settings(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "telegram": current_user.telegram_chat_id is not None,
        "email": True,
        "telegram_chat_id": current_user.telegram_chat_id,
    }


@router.put("/notifications/settings")
async def update_notification_settings(
    body: NotificationSettings, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict:
    from datetime import datetime, timezone

    if not body.telegram:
        current_user.telegram_chat_id = None
    current_user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"telegram": current_user.telegram_chat_id is not None, "email": body.email}
