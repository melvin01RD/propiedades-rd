import time
import logging
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("propiedades_rd.rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting simple en memoria.
    Límites:
    - /auth/register: 5 requests / 60s por IP
    - /auth/login: 10 requests / 60s por IP
    - Global: 100 requests / 60s por IP
    """

    LIMITS = {
        "/auth/register": (5, 60),
        "/auth/login": (10, 60),
    }
    GLOBAL_LIMIT = (100, 60)

    def __init__(self, app):
        super().__init__(app)
        self._requests: dict = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        now = time.time()
        window_start = now - window
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        if len(self._requests[key]) >= limit:
            oldest = self._requests[key][0]
            retry_after = int(oldest + window - now) + 1
            return True, retry_after

        self._requests[key].append(now)
        return False, 0

    async def dispatch(self, request: Request, call_next) -> Response:
        # Saltar health check y docs
        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        ip = self._get_client_ip(request)
        path = request.url.path

        # Rate limit específico por endpoint
        if path in self.LIMITS:
            limit, window = self.LIMITS[path]
            key = f"{ip}:{path}"
            limited, retry_after = self._is_rate_limited(key, limit, window)
            if limited:
                logger.warning(f"Rate limit hit: {ip} on {path}")
                return JSONResponse(
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                    content={
                        "error": {
                            "code": 429,
                            "message": f"Too many requests. Retry after {retry_after}s",
                            "path": path,
                        }
                    },
                )

        # Rate limit global
        global_key = f"{ip}:global"
        global_limit, global_window = self.GLOBAL_LIMIT
        limited, retry_after = self._is_rate_limited(global_key, global_limit, global_window)
        if limited:
            logger.warning(f"Global rate limit hit: {ip}")
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={
                    "error": {
                        "code": 429,
                        "message": f"Too many requests. Retry after {retry_after}s",
                        "path": path,
                    }
                },
            )

        return await call_next(request)
