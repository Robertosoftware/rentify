"""Deduplication logic for scraped listings."""
import logging
from datetime import datetime, timedelta, timezone

log = logging.getLogger(__name__)


async def upsert_listing(listing_data: dict, db_session) -> tuple[bool, bool]:
    """
    Upsert a listing into the database.
    Returns (is_new: bool, was_updated: bool).
    Uses ON CONFLICT (source_site, source_id) DO UPDATE.
    """
    from sqlmodel import select
    from backend.app.models.listing import Listing

    result = await db_session.execute(
        select(Listing).where(
            Listing.source_site == listing_data["source_site"],
            Listing.source_id == listing_data["source_id"],
        )
    )
    existing = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if existing:
        # Update mutable fields
        existing.last_seen_at = now
        existing.title = listing_data.get("title", existing.title)
        existing.price_eur = listing_data.get("price_eur_cents", existing.price_eur)
        existing.delisted_at = None  # Re-listed
        await db_session.commit()
        return False, True

    import uuid
    listing = Listing(
        id=uuid.uuid4(),
        source_site=listing_data["source_site"],
        source_id=listing_data["source_id"],
        source_url=listing_data["source_url"],
        title=listing_data["title"],
        price_eur=listing_data.get("price_eur_cents", 0),
        city=listing_data.get("city", ""),
        first_seen_at=now,
        last_seen_at=now,
        created_at=now,
        **{k: v for k, v in listing_data.items() if k not in (
            "source_site", "source_id", "source_url", "title",
            "price_eur_cents", "city", "scraped_at",
        )},
    )
    db_session.add(listing)
    await db_session.commit()
    return True, False


async def mark_delisted(source_site: str, active_ids: set[str], db_session, threshold_days: int = 7) -> int:
    """Mark listings as delisted if not seen in threshold_days."""
    from datetime import timedelta
    from sqlmodel import select
    from backend.app.models.listing import Listing

    cutoff = datetime.now(timezone.utc) - timedelta(days=threshold_days)
    result = await db_session.execute(
        select(Listing).where(
            Listing.source_site == source_site,
            Listing.delisted_at.is_(None),
            Listing.last_seen_at < cutoff,
        )
    )
    stale = result.scalars().all()
    count = 0
    for listing in stale:
        if listing.source_id not in active_ids:
            listing.delisted_at = datetime.now(timezone.utc)
            count += 1
    await db_session.commit()
    return count
