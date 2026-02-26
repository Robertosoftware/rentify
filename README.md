# Rentify
Find rental homes across Europe in one place, match them to user preferences, and deliver instant alerts.

## Architecture Overview
Rentify is built as a modular MVP with five core pieces:

- `frontend` (Vue 3 + Vite): user-facing app for signup/login, preferences, listings, and billing flows.
- `backend` (FastAPI + SQLModel): auth, billing, preferences, admin, notifications, GDPR, and observability APIs.
- `scrapers` (Python): source-specific parsers that normalize listings from multiple rental sites.
- `worker` (Dramatiq + Redis): async jobs for matching and notification delivery.
- `postgres` + `redis`: durable data storage + queue/cache/rate-limit backbone.

```mermaid
flowchart LR
  U[User] --> FE[Frontend :5173]
  FE --> API[FastAPI Backend :8000]
  API --> DB[(PostgreSQL)]
  API --> R[(Redis)]
  SW[Scraper Worker] --> DB
  SW --> R
  W[Dramatiq Worker] --> DB
  W --> R
  W --> N[Telegram / Email]
```

## Quick Start
Prerequisites: Docker + Docker Compose, GNU Make.

```bash
cp .env.example .env
make dev
```

Open:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

Optional: seed a demo user.

```bash
make seed
```

## Running Tests
Run everything:

```bash
make test
```

Run targeted checks:

```bash
make test-backend
make test-frontend
make lint
make pre-commit
```

## API Documentation
Start the backend and open:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Health check: `http://localhost:8000/health`
- Metrics: `http://localhost:8000/metrics`

Main API groups:

- Auth: `/auth/*`
- Billing + Stripe webhook: `/billing/*`, `/stripe/webhook`
- Preferences: `/preferences*`
- Listings + matches: `/listings*`, `/matches`
- Notifications: `/notifications/*`
- Admin: `/admin/*`
- GDPR: `/gdpr/*`

## Project Structure
Current scaffold (aligned to the `rentifyv2.md` blueprint):

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── db/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── services/
│   │   ├── tasks/
│   │   ├── workers/
│   │   ├── config.py
│   │   └── main.py
│   ├── alembic/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── vitest.config.ts
├── scrapers/
│   ├── src/
│   │   ├── anti_detection/
│   │   ├── models/
│   │   ├── scrapers/
│   │   ├── base_scraper.py
│   │   ├── deduplicator.py
│   │   ├── robots_checker.py
│   │   └── worker.py
│   ├── tests/
│   │   └── fixtures/
│   └── output/
├── infra/
│   ├── k8s/
│   └── terraform/
├── .devcontainer/
├── .github/
├── .env.example
├── docker-compose.dev.yml
├── Makefile
├── rentifyv2.md
└── README.md
```

## Environment Variables
Use `.env.example` as the source of truth for local development.

| Variable | Description | Example / Default |
|---|---|---|
| `DATABASE_URL` | Async DB URL for app runtime | `postgresql+asyncpg://postgres:password@localhost:5432/rentify` |
| `DATABASE_URL_SYNC` | Sync DB URL for scripts/migrations | `postgresql://postgres:password@localhost:5432/rentify` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET` | JWT signing secret | `local-dev-secret-replace-in-prod` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRY_MINUTES` | Access token TTL (minutes) | `60` |
| `JWT_REFRESH_EXPIRY_DAYS` | Refresh token TTL (days) | `30` |
| `PASSWORD_HASH_ALGORITHM` | Password hashing algorithm | `argon2` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `your-google-client-id` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | `your-google-client-secret` |
| `GOOGLE_REDIRECT_URI` | OAuth callback URI | `http://localhost:8000/auth/google/callback` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_placeholder` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_placeholder` |
| `STRIPE_PRICE_ID` | Stripe recurring price ID | `price_placeholder` |
| `MOCK_STRIPE` | Mock Stripe integration locally | `true` |
| `SENDGRID_API_KEY` | SendGrid API key | `SG.placeholder` |
| `SENDGRID_FROM_EMAIL` | Sender email for app notifications | `noreply@rentify.eu` |
| `MOCK_EMAIL` | Mock email sending locally | `true` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `placeholder` |
| `MOCK_TELEGRAM` | Mock Telegram sending locally | `true` |
| `SENTRY_DSN` | Sentry DSN for error tracking | empty |
| `LOG_LEVEL` | App log level | `INFO` |
| `LOG_FORMAT` | Log format (`json`/plain) | `json` |
| `ENABLE_PAID_GATE` | Enable paid-only gating middleware | `false` |
| `ENABLE_SCRAPING` | Enable scraping-related flows | `false` |
| `SCRAPER_SOURCES` | Comma-separated active scraper keys | `funda,pararius,kamernet,huurwoningen,housinganywhere,directbijeigenaar` |
| `SCRAPER_CITIES` | Comma-separated target cities | `amsterdam,rotterdam,utrecht,den-haag,eindhoven,groningen` |
| `SCRAPER_INTERVAL_SECONDS` | Scrape interval in seconds | `3600` |
| `SCRAPER_MAX_PAGES_PER_CITY` | Max pages scraped per city | `5` |
| `ENABLE_LIVE_SCRAPING` | Run real HTTP scraping vs fixtures | `false` |
| `SCRAPER_MIN_DELAY` | Min delay between requests | `2.0` |
| `SCRAPER_MAX_DELAY` | Max delay between requests | `5.0` |
| `PROXY_POOL_URL` | Optional proxy pool endpoint | empty |
| `PROXY_LIST` | Optional static proxy list | empty |
| `SONAR_TOKEN` | SonarCloud token (CI) | empty |
| `SONAR_ORGANIZATION` | SonarCloud org (CI) | empty |
| `SONAR_PROJECT_KEY` | SonarCloud project key (CI) | empty |

## Adding a New Scraper
1. Create `scrapers/src/scrapers/my_site.py` and extend `BaseScraper`.
2. Implement:
   - `build_search_url()`
   - `parse_search_results()`
   - `parse_listing_detail()`
3. Return normalized objects using `NormalizedListing`.
4. Add fixture HTML files in `scrapers/tests/fixtures/`.
5. Add parser tests, e.g. `scrapers/tests/test_my_site_parser.py`.
6. Register scraper in `SCRAPER_REGISTRY` (`scrapers/src/scrapers/__init__.py`, used by `scrapers/src/worker.py`).
7. Add the scraper key to `SCRAPER_SOURCES` in `.env`.
8. Validate by running:

```bash
pytest scrapers/
python scrapers/src/worker.py --sources my_site --cities amsterdam
```

## Deployment
See `infra/` for Terraform and Kubernetes skeletons. They are placeholders and not production-ready yet.

For production hardening, plan to add:

- managed Postgres + Redis
- secrets management
- HTTPS + domain routing
- background worker autoscaling
- proper observability and alerting

## License
MIT (see `LICENSE`).
