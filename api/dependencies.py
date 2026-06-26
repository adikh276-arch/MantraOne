from __future__ import annotations
from typing import AsyncGenerator, Annotated
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.session import get_async_session
from infrastructure.cache.redis_client import get_redis_client
from redis.asyncio import Redis
from core.events.publisher import EventPublisher

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session

async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = await get_redis_client()
    yield redis

async def get_event_publisher(redis: Redis = Depends(get_redis)) -> EventPublisher:
    return EventPublisher(redis)

def get_current_user(request: Request) -> dict:
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
