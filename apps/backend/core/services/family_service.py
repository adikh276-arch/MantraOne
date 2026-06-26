from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import Family, FamilyMember
from core.repositories.family_repository import FamilyRepository
from core.repositories.member_repository import MemberRepository
from core.providers.encryption_service import EncryptionService
from core.domain.enums import MemberRelationship

class FamilyService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._family_repo = FamilyRepository(db)
        self._member_repo = MemberRepository(db)
        self._enc = EncryptionService()

    async def create_family(self, name: str, firebase_uid: str, primary_member_name: str) -> Family:
        family = await self._family_repo.create(name=name, primary_user_id=firebase_uid)
        primary_member = FamilyMember(
            family_id=family.id,
            firebase_uid=firebase_uid,
            name=self._enc.encrypt(primary_member_name),
            relationship=MemberRelationship.SELF.value,
            is_primary=True,
        )
        await self._member_repo.save(primary_member)
        return family

    async def get_or_create_family_for_user(self, firebase_uid: str, default_name: str = "My Family") -> Family:
        family = await self._family_repo.get_by_primary_user(firebase_uid)
        if not family:
            family = await self.create_family(default_name, firebase_uid, "Primary Member")
        return family

    async def add_member(self, family_id: UUID, name: str, relationship: str, date_of_birth: str | None = None, gender: str | None = None) -> FamilyMember:
        member = FamilyMember(
            family_id=family_id,
            name=self._enc.encrypt(name),
            relationship=relationship,
            date_of_birth=self._enc.encrypt_optional(date_of_birth),
            gender=gender,
        )
        return await self._member_repo.save(member)
