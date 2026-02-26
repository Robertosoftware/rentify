import time

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

log = structlog.get_logger()

RATE_LIMIT_PATHS = {"/auth/login", "/auth/register"}
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 60  # seconds

_counters: dict = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in RATE_LIMIT_PATHS:
            ip = request.client.host if request.client else "unknown"
            key = f"{path}:{ip}"
            now = time.time()
            window_start = now - RATE_LIMIT_WINDOW
            calls = _counters.get(key, [])
            calls = [t for t in calls if t > window_start]
            if len(calls) >= RATE_LIMIT_MAX:
                log.warning("rate_limit.exceeded", path=path, ip=ip)
                return JSONResponse(status_code=429, content={"detail": "Too many requests. Try again later."})
            calls.append(now)
            _counters[key] = calls
        return await call_next(request)
