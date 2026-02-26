import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_db
from app.models.preference import Preference
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()
log = structlog.get_logger()

FREE_USER_LIMIT = 3
PAID_USER_LIMIT = 10


class PreferenceCreate(BaseModel):
    city: str
    country_code: str = "NL"
    min_price: int | None = None
    max_price: int
    min_rooms: float | None = None
    max_rooms: float | None = None
    min_size_sqm: int | None = None
    max_size_sqm: int | None = None
    pet_friendly: bool = False
    furnished: bool | None = None
    keywords: list[str] | None = None


class PreferenceUpdate(BaseModel):
    city: str | None = None
    country_code: str | None = None
    min_price: int | None = None
    max_price: int | None = None
    min_rooms: float | None = None
    max_rooms: float | None = None
    min_size_sqm: int | None = None
    max_size_sqm: int | None = None
    pet_friendly: bool | None = None
    furnished: bool | None = None
    keywords: list[str] | None = None


@router.get("/preferences")
async def list_preferences(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(
        select(Preference).where(Preference.user_id == current_user.id, Preference.is_active.is_(True))
    )
    prefs = result.scalars().all()
    return {"items": [_pref_to_dict(p) for p in prefs], "total": len(prefs)}


@router.post("/preferences", status_code=status.HTTP_201_CREATED)
async def create_preference(
    body: PreferenceCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(
        select(Preference).where(Preference.user_id == current_user.id, Preference.is_active.is_(True))
    )
    existing = result.scalars().all()

    limit = PAID_USER_LIMIT if current_user.subscription_status in ("trialing", "active") else FREE_USER_LIMIT
    if len(existing) >= limit:
        raise HTTPException(status_code=403, detail=f"Preference limit reached ({limit} max)")

    now = datetime.now(timezone.utc)
    pref = Preference(
        id=uuid.uuid4(),
        user_id=current_user.id,
        created_at=now,
        updated_at=now,
        **body.model_dump(),
    )
    db.add(pref)
    await db.commit()
    await db.refresh(pref)
    log.info("preference.created", user_id=str(current_user.id), pref_id=str(pref.id))
    return _pref_to_dict(pref)


@router.put("/preferences/{pref_id}")
async def update_preference(
    pref_id: uuid.UUID,
    body: PreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Preference).where(Preference.id == pref_id, Preference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(pref, field, value)
    pref.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(pref)
    return _pref_to_dict(pref)


@router.delete("/preferences/{pref_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preference(
    pref_id: uuid.UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    result = await db.execute(select(Preference).where(Preference.id == pref_id, Preference.user_id == current_user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    pref.is_active = False
    pref.updated_at = datetime.now(timezone.utc)
    await db.commit()


def _pref_to_dict(p: Preference) -> dict:
    return {
        "id": str(p.id),
        "user_id": str(p.user_id),
        "city": p.city,
        "country_code": p.country_code,
        "min_price": p.min_price,
        "max_price": p.max_price,
        "min_rooms": p.min_rooms,
        "max_rooms": p.max_rooms,
        "min_size_sqm": p.min_size_sqm,
        "max_size_sqm": p.max_size_sqm,
        "pet_friendly": p.pet_friendly,
        "furnished": p.furnished,
        "keywords": p.keywords,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }
