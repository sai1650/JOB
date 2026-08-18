import time
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict


class SimpleRateLimiterMiddleware(BaseHTTPMiddleware):
    """Very small in-memory rate limiter per-client IP.

    Limits requests to `max_requests` per `window_seconds`.
    Not suitable for multi-process deployments, but acceptable for local
    dev and simple production with a single process.
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._clients: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        client = request.client.host if request.client else "unknown"
        now = time.time()
        q = self._clients.get(client, [])
        # drop old
        q = [t for t in q if t > now - self.window]
        if len(q) >= self.max_requests:
            from starlette.responses import JSONResponse

            resp = JSONResponse(
                {"detail": "Too many requests"},
                status_code=429,
            )
            return resp
        q.append(now)
        self._clients[client] = q
        return await call_next(request)
