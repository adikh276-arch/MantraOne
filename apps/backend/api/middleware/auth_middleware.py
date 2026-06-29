from __future__ import annotations
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from infrastructure.cloud.firebase import verify_firebase_token
import structlog

logger = structlog.get_logger()


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path in ["/health", "/docs", "/openapi.json"] or request.url.path.startswith("/v1/internal/"):
            return await call_next(request)

        from config.settings import settings

        if settings.local_dev_mode:
            request.state.user = {"uid": "local-dev", "email": "dev@local.host"}
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(content="Unauthorized", status_code=401)

        token = auth_header.split(" ")[1]
        try:
            user = await verify_firebase_token(token)
            request.state.user = user
        except Exception as e:
            logger.warning("auth_failed", error=str(e))
            return Response(content="Invalid token", status_code=401)

        return await call_next(request)
