import uuid
from datetime import datetime, timezone

import structlog

import dramatiq

log = structlog.get_logger()


@dramatiq.actor(queue_name="matching")
def match_listing(listing_id: str) -> None:
    import asyncio

    asyncio.run(_match_listing_async(listing_id))


async def _match_listing_async(listing_id: str) -> None:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlmodel import select

    from app.db.session import AsyncSessionLocal
    from app.models.listing import Listing
    from app.models.match import Match
    from app.models.preference import Preference
    from app.services.matcher import MATCH_THRESHOLD, score_listing

    async with AsyncSessionLocal() as db:
        listing = await db.get(Listing, uuid.UUID(listing_id))
        if not listing:
            log.warning("match_listing.not_found", listing_id=listing_id)
            return

        result = await db.execute(
            select(Preference).where(
                Preference.city == listing.city,
                Preference.is_active.is_(True),
            )
        )
        prefs = result.scalars().all()

        for pref in prefs:
            sc = score_listing(listing, pref)
            if sc >= MATCH_THRESHOLD:
                existing = await db.execute(
                    select(Match).where(Match.user_id == pref.user_id, Match.listing_id == listing.id)
                )
                if existing.scalar_one_or_none():
                    continue

                match = Match(
                    id=uuid.uuid4(),
                    user_id=pref.user_id,
                    listing_id=listing.id,
                    preference_id=pref.id,
                    score=sc,
                    created_at=datetime.now(timezone.utc),
                )
                db.add(match)
                await db.commit()
                log.info("match.created", match_id=str(match.id), score=sc)
                notify_user.send(str(match.id))


@dramatiq.actor(queue_name="notifications")
def notify_user(match_id: str) -> None:
    import asyncio

    asyncio.run(_notify_user_async(match_id))


async def _notify_user_async(match_id: str) -> None:
    from sqlmodel import select

    from app.db.session import AsyncSessionLocal
    from app.models.listing import Listing
    from app.models.match import Match
    from app.models.user import User
    from app.services.email_service import send_email
    from app.services.telegram_service import send_telegram_message

    async with AsyncSessionLocal() as db:
        match = await db.get(Match, uuid.UUID(match_id))
        if not match:
            return
        user = await db.get(User, match.user_id)
        listing = await db.get(Listing, match.listing_id)
        if not user or not listing:
            return

        msg = (
            f"*New Rental Match!*\n"
            f"{listing.title}\n"
            f"Price: €{listing.price_eur // 100}/month\n"
            f"City: {listing.city}\n"
            f"[View listing]({listing.source_url})"
        )

        if user.telegram_chat_id:
            await send_telegram_message(user.telegram_chat_id, msg)
            match.notification_channel = "telegram"
        else:
            html = f"<h2>New Rental Match</h2><p>{listing.title}</p><p>Price: €{listing.price_eur // 100}/month</p><a href='{listing.source_url}'>View listing</a>"
            await send_email(user.email, "New Rental Match!", html)
            match.notification_channel = "email"

        match.notified = True
        match.notified_at = datetime.now(timezone.utc)
        await db.commit()


@dramatiq.actor(queue_name="notifications")
def send_trial_reminder(user_id: str, reminder_type: str) -> None:
    import asyncio

    asyncio.run(_send_trial_reminder_async(user_id, reminder_type))


async def _send_trial_reminder_async(user_id: str, reminder_type: str) -> None:
    from app.db.session import AsyncSessionLocal
    from app.models.user import User
    from app.services.email_service import send_email

    async with AsyncSessionLocal() as db:
        user = await db.get(User, uuid.UUID(user_id))
        if not user or user.deleted_at:
            return

        subjects = {
            "48h": "Your Rentify trial ends in 48 hours",
            "24h": "Last day of your Rentify trial!",
        }
        html = f"<p>Hi {user.full_name or 'there'},</p><p>Your 7-day trial {subjects.get(reminder_type, 'is ending soon')}. <a href='http://localhost:5173/dashboard'>Upgrade now</a> to keep getting matches.</p>"
        await send_email(user.email, subjects.get(reminder_type, "Trial ending"), html)
        log.info("trial_reminder.sent", user_id=user_id, type=reminder_type)
