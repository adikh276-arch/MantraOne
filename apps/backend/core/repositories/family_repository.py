from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import Family
from core.repositories.base import BaseRepository


class FamilyRepository(BaseRepository[Family]):
    model = Family

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_primary_user(self, firebase_uid: str) -> Family | None:
        result = await self._db.execute(
            select(Family).where(
                Family.primary_user_id == firebase_uid,
                Family.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_no_scope(self, family_id: UUID) -> Family | None:
        result = await self._db.execute(
            select(Family).where(
                Family.id == family_id,
                Family.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, primary_user_id: str) -> Family:
        family = Family(name=name, primary_user_id=primary_user_id)
        return await self.save(family)
