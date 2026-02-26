import structlog
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.feature_flag_service import get_flag

log = structlog.get_logger()


async def paid_gate(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> User:
    gate_enabled = await get_flag("paid_gate_enabled", db)
    if not gate_enabled:
        return current_user
    if current_user.subscription_status in ("trialing", "active"):
        return current_user
    raise HTTPException(
        status_code=403,
        detail="Active subscription required",
        headers={"X-Upgrade-URL": "/billing/create-checkout-session"},
    )
