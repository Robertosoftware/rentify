import os
from functools import lru_cache


class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/rentify")
    DATABASE_URL_SYNC: str = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:password@localhost:5432/rentify")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "local-dev-secret-replace-in-prod")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_MINUTES: int = int(os.getenv("JWT_EXPIRY_MINUTES", "60"))
    JWT_REFRESH_EXPIRY_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRY_DAYS", "30"))
    PASSWORD_HASH_ALGORITHM: str = os.getenv("PASSWORD_HASH_ALGORITHM", "argon2")

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")
    STRIPE_PRICE_ID: str = os.getenv("STRIPE_PRICE_ID", "price_placeholder")
    MOCK_STRIPE: bool = os.getenv("MOCK_STRIPE", "true").lower() == "true"

    # SendGrid
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "SG.placeholder")
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "noreply@rentify.eu")
    MOCK_EMAIL: bool = os.getenv("MOCK_EMAIL", "true").lower() == "true"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "placeholder")
    MOCK_TELEGRAM: bool = os.getenv("MOCK_TELEGRAM", "true").lower() == "true"

    # Observability
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    # Feature flags
    ENABLE_PAID_GATE: bool = os.getenv("ENABLE_PAID_GATE", "false").lower() == "true"
    ENABLE_SCRAPING: bool = os.getenv("ENABLE_SCRAPING", "false").lower() == "true"

    # Scraper settings
    SCRAPER_SOURCES: str = os.getenv("SCRAPER_SOURCES", "funda,pararius,kamernet,huurwoningen,housinganywhere,directbijeigenaar")
    SCRAPER_CITIES: str = os.getenv("SCRAPER_CITIES", "amsterdam,rotterdam,utrecht,den-haag,eindhoven,groningen")
    SCRAPER_INTERVAL_SECONDS: int = int(os.getenv("SCRAPER_INTERVAL_SECONDS", "3600"))
    SCRAPER_MAX_PAGES_PER_CITY: int = int(os.getenv("SCRAPER_MAX_PAGES_PER_CITY", "5"))
    ENABLE_LIVE_SCRAPING: bool = os.getenv("ENABLE_LIVE_SCRAPING", "false").lower() == "true"
    SCRAPER_MIN_DELAY: float = float(os.getenv("SCRAPER_MIN_DELAY", "2.0"))
    SCRAPER_MAX_DELAY: float = float(os.getenv("SCRAPER_MAX_DELAY", "5.0"))
    PROXY_POOL_URL: str = os.getenv("PROXY_POOL_URL", "")
    PROXY_LIST: str = os.getenv("PROXY_LIST", "")


@lru_cache
def get_settings() -> Settings:
    return Settings()
