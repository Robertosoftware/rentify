import uuid
from datetime import datetime, timedelta, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter()
settings = get_settings()
log = structlog.get_logger()
security = HTTPBearer()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    gdpr_consent: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    id: str
    email: str
    access_token: str
    refresh_token: str


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=RegisterResponse)
async def register(body: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)) -> RegisterResponse:
    if not body.gdpr_consent:
        raise HTTPException(status_code=422, detail="GDPR consent is required to register")

    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")

    result = await db.execute(select(User).where(User.email == body.email, User.deleted_at.is_(None)))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        id=uuid.uuid4(),
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        gdpr_consent_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in prod
        samesite="lax",
        max_age=settings.JWT_REFRESH_EXPIRY_DAYS * 86400,
    )

    log.info("auth.register", user_id=str(user.id), email=user.email)
    return RegisterResponse(id=str(user.id), email=user.email, access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email, User.deleted_at.is_(None)))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.JWT_REFRESH_EXPIRY_DAYS * 86400,
    )

    log.info("auth.login", user_id=str(user.id))
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request) -> TokenResponse:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token(user_id)
    return TokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, _: User = Depends(get_current_user)) -> None:
    response.delete_cookie("refresh_token")


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "auth_provider": current_user.auth_provider,
        "subscription_status": current_user.subscription_status,
        "trial_ends_at": current_user.trial_ends_at.isoformat() if current_user.trial_ends_at else None,
        "telegram_chat_id": current_user.telegram_chat_id,
        "is_admin": current_user.is_admin,
        "gdpr_consent_at": current_user.gdpr_consent_at.isoformat() if current_user.gdpr_consent_at else None,
        "created_at": current_user.created_at.isoformat(),
    }
