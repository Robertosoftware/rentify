import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, func, select

from app.db.session import get_db
from app.middleware.paid_gate import paid_gate
from app.models.listing import Listing
from app.models.match import Match
from app.models.user import User

router = APIRouter()
log = structlog.get_logger()


@router.get("/listings")
async def list_listings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    city: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    current_user: User = Depends(paid_gate),
    db: AsyncSession = Depends(get_db),
) -> dict:
    query = select(Listing).where(col(Listing.delisted_at).is_(None))
    if city:
        query = query.where(col(Listing.city).ilike(f"%{city}%"))
    if min_price is not None:
        query = query.where(Listing.price_eur >= min_price)
    if max_price is not None:
        query = query.where(Listing.price_eur <= max_price)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    offset = (page - 1) * per_page
    result = await db.execute(query.offset(offset).limit(per_page))
    listings = result.scalars().all()
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return {
        "items": [_listing_to_dict(listing) for listing in listings],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


@router.get("/listings/{listing_id}")
async def get_listing(
    listing_id: uuid.UUID,
    current_user: User = Depends(paid_gate),
    db: AsyncSession = Depends(get_db),
) -> dict:
    listing = await db.get(Listing, listing_id)
    if not listing or listing.delisted_at:
        raise HTTPException(status_code=404, detail="Listing not found")
    return _listing_to_dict(listing)


@router.get("/matches")
async def list_matches(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    unread_only: bool = False,
    current_user: User = Depends(paid_gate),
    db: AsyncSession = Depends(get_db),
) -> dict:
    query = select(Match).where(Match.user_id == current_user.id)
    if unread_only:
        query = query.where(col(Match.notified).is_(False))
    query = query.order_by(col(Match.created_at).desc())

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()
    offset = (page - 1) * per_page
    result = await db.execute(query.offset(offset).limit(per_page))
    matches = result.scalars().all()
    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return {
        "items": [
            {
                "id": str(m.id),
                "listing_id": str(m.listing_id),
                "preference_id": str(m.preference_id),
                "score": m.score,
                "notified": m.notified,
                "notification_channel": m.notification_channel,
                "created_at": m.created_at.isoformat(),
            }
            for m in matches
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


def _listing_to_dict(listing: Listing) -> dict:
    return {
        "id": str(listing.id),
        "source_site": listing.source_site,
        "source_url": listing.source_url,
        "title": listing.title,
        "description": listing.description,
        "price_eur_cents": listing.price_eur,
        "price_eur": listing.price_eur / 100,
        "price_type": listing.price_type,
        "rooms": listing.rooms,
        "bedrooms": listing.bedrooms,
        "size_sqm": listing.size_sqm,
        "city": listing.city,
        "neighborhood": listing.neighborhood,
        "postal_code": listing.postal_code,
        "country_code": listing.country_code,
        "address": listing.address,
        "pet_friendly": listing.pet_friendly,
        "furnished": listing.furnished,
        "energy_label": listing.energy_label,
        "available_from": listing.available_from.isoformat() if listing.available_from else None,
        "rental_agent": listing.rental_agent,
        "image_urls": listing.image_urls or [],
        "first_seen_at": listing.first_seen_at.isoformat(),
    }
