import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

log = structlog.get_logger()

app = FastAPI(
    title="Rentify API",
    description="Rental listing aggregator API",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    log.info("rentify.startup", env="development")

    if settings.SENTRY_DSN:
        import sentry_sdk

        sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)


# --- Routers ---
from app.api import auth, billing, preferences, notifications, admin, gdpr, oauth  # noqa: E402

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(oauth.router, prefix="/auth", tags=["auth"])
app.include_router(billing.router, tags=["billing"])
app.include_router(preferences.router, tags=["preferences"])
app.include_router(notifications.router, tags=["notifications"])
app.include_router(admin.router, tags=["admin"])
app.include_router(gdpr.router, tags=["gdpr"])


@app.get("/health", tags=["health"])
async def health() -> dict:
    from sqlalchemy import text

    from app.db.session import AsyncSessionLocal

    db_status = "ok"
    redis_status = "ok"

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
    except Exception:
        redis_status = "error"

    return {"status": "ok", "db": db_status, "redis": redis_status}
