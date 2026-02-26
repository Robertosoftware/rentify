import json
import uuid
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import get_settings
from app.models.user import User

settings = get_settings()
log = structlog.get_logger()

_PROCESSED_EVENTS_PREFIX = "stripe:event:"


async def _get_redis():
    import redis.asyncio as aioredis
    return aioredis.from_url(settings.REDIS_URL)


async def create_checkout_session(user: User, db: AsyncSession) -> dict:
    if settings.MOCK_STRIPE:
        mock_session_id = f"cs_test_mock_{uuid.uuid4().hex[:16]}"
        log.info("stripe.mock_checkout", user_id=str(user.id), session_id=mock_session_id)
        return {
            "session_id": mock_session_id,
            "url": f"https://checkout.stripe.com/mock/{mock_session_id}",
        }

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY

    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": str(user.id)})
        user.stripe_customer_id = customer.id
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()

    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": settings.STRIPE_PRICE_ID, "quantity": 1}],
        mode="subscription",
        subscription_data={"trial_period_days": 7},
        success_url="http://localhost:5173/dashboard?checkout=success",
        cancel_url="http://localhost:5173/dashboard?checkout=cancelled",
    )
    return {"session_id": session.id, "url": session.url}


async def create_portal_session(user: User, db: AsyncSession) -> dict:
    if settings.MOCK_STRIPE:
        return {"url": "https://billing.stripe.com/mock/portal"}

    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url="http://localhost:5173/dashboard",
    )
    return {"url": session.url}


async def handle_webhook_event(body: bytes, signature: str, db: AsyncSession) -> None:
    if settings.MOCK_STRIPE:
        try:
            data = json.loads(body)
            event_id = data.get("id", "mock_event")
            event_type = data.get("type", "unknown")
        except Exception:
            return
    else:
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            event = stripe.Webhook.construct_event(body, signature, settings.STRIPE_WEBHOOK_SECRET)
        except Exception as e:
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {e}")
        event_id = event["id"]
        event_type = event["type"]
        data = event

    # Idempotency check
    r = await _get_redis()
    key = f"{_PROCESSED_EVENTS_PREFIX}{event_id}"
    already_processed = await r.get(key)
    if already_processed:
        log.info("stripe.webhook_duplicate", event_id=event_id)
        await r.aclose()
        return
    await r.set(key, "1", ex=86400)
    await r.aclose()

    log.info("stripe.webhook", event_type=event_type, event_id=event_id)

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(data, db)
    elif event_type in ("invoice.paid",):
        await _handle_invoice_paid(data, db)
    elif event_type == "invoice.payment_failed":
        await _handle_payment_failed(data, db)
    elif event_type in ("customer.subscription.deleted",):
        await _handle_subscription_deleted(data, db)
    elif event_type == "customer.subscription.updated":
        await _handle_subscription_updated(data, db)


async def _handle_checkout_completed(data: dict, db: AsyncSession) -> None:
    customer_id = data.get("data", {}).get("object", {}).get("customer") or data.get("customer")
    if not customer_id:
        return
    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    user = result.scalar_one_or_none()
    if user:
        user.subscription_status = "trialing"
        user.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=7)
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()


async def _handle_invoice_paid(data: dict, db: AsyncSession) -> None:
    customer_id = data.get("data", {}).get("object", {}).get("customer") or data.get("customer")
    if not customer_id:
        return
    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    user = result.scalar_one_or_none()
    if user:
        user.subscription_status = "active"
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()


async def _handle_payment_failed(data: dict, db: AsyncSession) -> None:
    customer_id = data.get("data", {}).get("object", {}).get("customer") or data.get("customer")
    if not customer_id:
        return
    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    user = result.scalar_one_or_none()
    if user:
        user.subscription_status = "past_due"
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()


async def _handle_subscription_deleted(data: dict, db: AsyncSession) -> None:
    customer_id = data.get("data", {}).get("object", {}).get("customer") or data.get("customer")
    if not customer_id:
        return
    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    user = result.scalar_one_or_none()
    if user:
        user.subscription_status = "canceled"
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()


async def _handle_subscription_updated(data: dict, db: AsyncSession) -> None:
    obj = data.get("data", {}).get("object", {})
    customer_id = obj.get("customer") or data.get("customer")
    status = obj.get("status")
    if not customer_id or not status:
        return
    result = await db.execute(select(User).where(User.stripe_customer_id == customer_id))
    user = result.scalar_one_or_none()
    if user and status in ("trialing", "active", "past_due", "canceled"):
        user.subscription_status = status
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()


async def cancel_subscription(stripe_customer_id: str) -> None:
    if settings.MOCK_STRIPE:
        return
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    subscriptions = stripe.Subscription.list(customer=stripe_customer_id, status="active")
    for sub in subscriptions.data:
        stripe.Subscription.delete(sub.id)
