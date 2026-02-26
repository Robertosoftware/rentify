import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_db
from app.models.match import Match
from app.models.notification import Notification
from app.models.preference import Preference
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()
log = structlog.get_logger()


@router.get("/gdpr/export")
async def export_data(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    prefs_result = await db.execute(select(Preference).where(Preference.user_id == current_user.id))
    prefs = prefs_result.scalars().all()

    matches_result = await db.execute(select(Match).where(Match.user_id == current_user.id))
    matches = matches_result.scalars().all()

    notifs_result = await db.execute(select(Notification).where(Notification.user_id == current_user.id))
    notifs = notifs_result.scalars().all()

    return {
        "profile": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "auth_provider": current_user.auth_provider,
            "subscription_status": current_user.subscription_status,
            "created_at": current_user.created_at.isoformat(),
            "gdpr_consent_at": current_user.gdpr_consent_at.isoformat() if current_user.gdpr_consent_at else None,
        },
        "preferences": [{"id": str(p.id), "city": p.city, "max_price": p.max_price} for p in prefs],
        "matches": [{"id": str(m.id), "listing_id": str(m.listing_id), "score": m.score} for m in matches],
        "notifications": [{"id": str(n.id), "channel": n.channel, "type": n.type, "status": n.status} for n in notifs],
    }


@router.delete("/gdpr/delete-account", status_code=status.HTTP_202_ACCEPTED)
async def delete_account(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    current_user.deleted_at = now
    current_user.email = f"deleted_{current_user.id}@deleted.invalid"
    current_user.full_name = None
    current_user.hashed_password = None
    current_user.telegram_chat_id = None
    current_user.google_id = None
    current_user.updated_at = now

    if current_user.stripe_customer_id and not __import__("app.config", fromlist=["get_settings"]).get_settings().MOCK_STRIPE:
        from app.services.stripe_service import cancel_subscription
        await cancel_subscription(current_user.stripe_customer_id)

    await db.commit()
    log.info("gdpr.account_deleted", user_id=str(current_user.id))
    return {"detail": "Account scheduled for deletion"}
