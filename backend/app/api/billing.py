import json
import uuid
from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.stripe_service import (
    create_checkout_session,
    create_portal_session,
    handle_webhook_event,
)

router = APIRouter()
settings = get_settings()
log = structlog.get_logger()


@router.post("/billing/create-checkout-session")
async def checkout_session(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    result = await create_checkout_session(current_user, db)
    return result


@router.post("/billing/create-portal-session")
async def portal_session(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    result = await create_portal_session(current_user, db)
    return result


@router.get("/billing/status")
async def billing_status(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "subscription_status": current_user.subscription_status,
        "trial_ends_at": current_user.trial_ends_at.isoformat() if current_user.trial_ends_at else None,
        "current_period_end": None,
    }


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    body = await request.body()
    sig = request.headers.get("stripe-signature", "")
    await handle_webhook_event(body, sig, db)
    return {"status": "ok"}
