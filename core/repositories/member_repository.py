from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from infrastructure.database.models import FamilyMember
from core.repositories.base import BaseRepository

class MemberRepository(BaseRepository[FamilyMember]):
    model = FamilyMember

    async def get_by_firebase_uid(self, firebase_uid: str, family_id: UUID | None = None) -> FamilyMember | None:
        conditions = [FamilyMember.firebase_uid == firebase_uid, FamilyMember.deleted_at.is_(None)]
        if family_id:
            conditions.append(FamilyMember.family_id == family_id)
        result = await self._db.execute(select(FamilyMember).where(*conditions))
        return result.scalar_one_or_none()

    async def list_by_family(self, family_id: UUID) -> list[FamilyMember]:
        result = await self._db.execute(
            select(FamilyMember).where(
                FamilyMember.family_id == family_id,
                FamilyMember.deleted_at.is_(None),
            ).order_by(FamilyMember.is_primary.desc(), FamilyMember.created_at)
        )
        return list(result.scalars().all())

    async def get_primary_member(self, family_id: UUID) -> FamilyMember | None:
        result = await self._db.execute(
            select(FamilyMember).where(
                FamilyMember.family_id == family_id,
                FamilyMember.is_primary.is_(True),
                FamilyMember.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_active_members_all_families(self) -> list[FamilyMember]:
        result = await self._db.execute(
            select(FamilyMember).where(
                FamilyMember.deleted_at.is_(None),
                FamilyMember.firebase_uid.is_not(None),
            )
        )
        return list(result.scalars().all())
