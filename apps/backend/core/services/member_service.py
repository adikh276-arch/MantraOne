from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import FamilyMember
from core.repositories.member_repository import MemberRepository
from core.providers.encryption_service import EncryptionService

class MemberService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._member_repo = MemberRepository(db)
        self._enc = EncryptionService()

    async def get_member(self, member_id: UUID, family_id: UUID) -> FamilyMember | None:
        member = await self._member_repo.get_by_id(member_id, family_id)
        if member:
            member.name = self._enc.decrypt(member.name)
            if member.date_of_birth:
                member.date_of_birth = self._enc.decrypt(member.date_of_birth)
        return member

    async def link_firebase_uid(self, member_id: UUID, family_id: UUID, firebase_uid: str) -> FamilyMember | None:
        member = await self._member_repo.get_by_id(member_id, family_id)
        if member:
            member.firebase_uid = firebase_uid
            await self._member_repo.save(member)
        return member
