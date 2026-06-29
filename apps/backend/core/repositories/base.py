from __future__ import annotations
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import TypeVar, Generic, Type
from infrastructure.database.session import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: Type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, entity_id: UUID, family_id: UUID) -> ModelT | None:
        result = await self._db.execute(
            select(self.model).where(
                getattr(self.model, "id") == entity_id,  # type: ignore
                getattr(self.model, "family_id") == family_id,  # type: ignore
                getattr(self.model, "deleted_at").is_(None) if hasattr(self.model, "deleted_at") else True,  # type: ignore
            )
        )
        return result.scalar_one_or_none()

    async def save(self, entity: ModelT) -> ModelT:
        self._db.add(entity)
        await self._db.flush()
        await self._db.refresh(entity)
        return entity

    async def soft_delete(self, entity: ModelT) -> None:
        setattr(entity, "deleted_at", datetime.now(timezone.utc))  # type: ignore
        await self._db.flush()
