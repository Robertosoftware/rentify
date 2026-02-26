import time
import uuid

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time.time()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)
        log.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
            request_id=request_id,
        )
        structlog.contextvars.clear_contextvars()
        response.headers["X-Request-ID"] = request_id
        return response
