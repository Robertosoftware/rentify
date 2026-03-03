# Rentify MVP — Implementation Progress

> Last updated: 2026-03-03. Pre-commit: ruff ✅ ruff-format ✅ mypy ✅. Backend tests: 27/27 ✅

---

## ✅ Completed

### Backend
- [x] All 6 SQLModel models (`user`, `listing`, `match`, `preference`, `notification`, `feature_flag`)
- [x] Alembic migration `001_initial_schema.py` — all tables, indexes, default feature flags
- [x] `app/db/session.py` — async SQLAlchemy session factory
- [x] API routes: `auth`, `oauth`, `billing`, `preferences`, `listings`, `notifications`, `admin`, `gdpr`
- [x] Services: `auth_service`, `stripe_service`, `email_service`, `telegram_service`, `matcher`, `feature_flag_service`
- [x] Middleware: `cors`, `rate_limit`, `paid_gate`, `logging_mw`
- [x] Workers: Dramatiq broker + `match_listing` / `notify_user` / `send_trial_reminder` actors
- [x] 27 backend unit tests passing (auth, billing, preferences, feature flags, matcher, paid gate, health)
- [x] Integration test skeleton (`tests/integration/test_db_integration.py`)

### Scrapers
- [x] `BaseScraper` with aiohttp, retry, throttling, robots.txt check
- [x] All 6 scrapers: `funda`, `pararius`, `kamernet`, `huurwoningen`, `housinganywhere`, `direct_bij_eigenaar`
- [x] Anti-detection: `user_agents`, `agent_rotator`, `request_throttler`, `proxy_rotator`
- [x] `deduplicator.py` — upsert + mark-delisted logic
- [x] `robots_checker.py`
- [x] Scraper tests: funda, pararius, kamernet, huurwoningen, deduplicator, agent_rotator
- [x] HTML fixtures for all 6 scrapers (search results) + funda/pararius listing pages

### Frontend
- [x] 7 pages: `Landing`, `Signup`, `Login`, `Dashboard`, `Preferences`, `Privacy`, `NotFound`
- [x] 6 components: `GoogleSignIn`, `TrialBanner`, `ListingCard`, `LoadingSpinner`, `ErrorAlert`, `CookieConsent`
- [x] 2 Pinia stores: `auth`, `user`
- [x] `useApi.ts` composable — Axios with JWT interceptor + auto-refresh
- [x] `router/index.ts` — 7 routes with auth guards
- [x] 3 frontend tests: `Landing.test.ts`, `Signup.test.ts`, `Dashboard.test.ts`

### DevOps / Config
- [x] `docker-compose.dev.yml` — postgres, redis, backend, frontend, worker
- [x] `backend/Dockerfile`
- [x] `.devcontainer/Dockerfile` + `postCreate.sh`
- [x] `.github/workflows/ci.yml` + `release.yml`
- [x] `Makefile` with dev, test, lint, migrate, seed targets
- [x] `.pre-commit-config.yaml` — ruff, ruff-format, mypy (all passing)
- [x] `sonar-project.properties`
- [x] `.env.example`

---

## ❌ Missing / Incomplete

### High priority
- [x] **`frontend/Dockerfile`**
- [x] **`scrapers/Dockerfile`**
- [x] **`scrapers/tests/test_housinganywhere_parser.py`** — 4 tests, all passing
- [x] **`scrapers/tests/test_direct_bij_eigenaar_parser.py`** — 5 tests, all passing
- [x] **`scrapers/pyproject.toml`** — added `pythonpath = [".."]` so all scraper tests resolve imports correctly

### Medium priority
- [ ] **`frontend/tsconfig.app.json` + `tsconfig.node.json`** — spec requires split tsconfig; only `tsconfig.json` exists
- [ ] **`frontend/env.d.ts`** — Vue SFC TypeScript shim (`/// <reference types="vite/client" />`)
- [ ] **FastAPI `on_event` deprecation** — `app/main.py` uses `@app.on_event("startup"/"shutdown")`; should migrate to `lifespan=` context manager (21 deprecation warnings in test output)
- [ ] **Redis `aclose()` vs `close()`** — `main.py:75` changed to `close()` to satisfy mypy stubs, but redis 5.x deprecates `close()` in favour of `aclose()`; fix by adding `# type: ignore[attr-defined]` and reverting to `aclose()`

### Low priority
- [ ] **`frontend` uses npm** (`package-lock.json`) — spec says pnpm (`pnpm-lock.yaml`); functional but inconsistent with spec
- [ ] **`frontend/eslint.config.ts`** — spec calls for flat ESLint 9 config in TypeScript; current setup uses JS-based config
- [ ] **Fixture HTML files for listing detail pages** — `kamernet_listing_page.html` and `huurwoningen_listing_page.html` missing (funda + pararius have them)
- [ ] **`infra/terraform/main.tf`** and **`infra/k8s/README.md`** — spec says skeleton only; may be empty/absent

---

## Known Warnings (non-blocking)
- `passlib` uses deprecated `crypt` module (Python 3.13 removal) — upstream issue, no action needed
- `python-jose` uses `datetime.utcnow()` internally — upstream issue
- FastAPI `on_event` deprecation — 21 warnings; addressable with lifespan handler refactor
