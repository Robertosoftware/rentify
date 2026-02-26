import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import create_access_token, create_refresh_token

router = APIRouter()
settings = get_settings()
log = structlog.get_logger()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/google")
async def google_login() -> RedirectResponse:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")

    params = (
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
    )
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}{params}")


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)) -> RedirectResponse:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured")

    import httpx

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")

        tokens = token_resp.json()
        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info")

        google_user = user_resp.json()

    google_id = google_user["sub"]
    email = google_user.get("email")
    full_name = google_user.get("name")

    result = await db.execute(select(User).where(User.google_id == google_id, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()

    if not user:
        result = await db.execute(select(User).where(User.email == email, User.deleted_at.is_(None)))
        user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            auth_provider="google",
            google_id=google_id,
            gdpr_consent_at=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.google_id:
        user.google_id = google_id
        user.auth_provider = "google"
        await db.commit()

    access_token = create_access_token(str(user.id))
    log.info("auth.google_login", user_id=str(user.id))
    return RedirectResponse(url=f"http://localhost:5173/dashboard#token={access_token}")
