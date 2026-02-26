import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.db.session import get_db
from app.models.feature_flag import FeatureFlag
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()
log = structlog.get_logger()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


class FlagUpdate(BaseModel):
    enabled: bool


@router.get("/admin/feature-flags")
async def list_flags(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(FeatureFlag))
    flags = result.scalars().all()
    return {"items": [_flag_to_dict(f) for f in flags]}


@router.put("/admin/feature-flags/{name}")
async def update_flag(
    name: str, body: FlagUpdate, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
) -> dict:
    from datetime import datetime, timezone

    result = await db.execute(select(FeatureFlag).where(FeatureFlag.name == name))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    flag.enabled = body.enabled
    flag.updated_by = admin.id
    flag.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(flag)
    log.info("feature_flag.updated", name=name, enabled=body.enabled, updated_by=str(admin.id))
    return _flag_to_dict(flag)


@router.get("/admin/users")
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    offset = (page - 1) * per_page
    count_result = await db.execute(select(func.count(User.id)).where(User.deleted_at.is_(None)))
    total = count_result.scalar_one()
    result = await db.execute(select(User).where(User.deleted_at.is_(None)).offset(offset).limit(per_page))
    users = result.scalars().all()
    pages = (total + per_page - 1) // per_page
    return {
        "items": [
            {
                "id": str(u.id),
                "email": u.email,
                "subscription_status": u.subscription_status,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


def _flag_to_dict(f: FeatureFlag) -> dict:
    return {
        "id": str(f.id),
        "name": f.name,
        "enabled": f.enabled,
        "description": f.description,
        "updated_by": str(f.updated_by) if f.updated_by else None,
        "created_at": f.created_at.isoformat(),
        "updated_at": f.updated_at.isoformat(),
    }
