from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from core.repositories.audit_repository import AuditRepository
from core.domain.enums import ActorRole, MemoryOperationType

class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = AuditRepository(db)

    async def log_phi_access(self, actor_firebase_uid: str, actor_role: ActorRole, action: str, resource_type: str, result: str, family_id: UUID | None = None, member_id: UUID | None = None, resource_id: UUID | None = None) -> None:
        await self._repo.log_phi_access(
            actor_firebase_uid=actor_firebase_uid,
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            result=result,
            family_id=family_id,
            member_id=member_id,
            resource_id=resource_id,
        )

    async def log_memory_operation(self, family_id: UUID, operation_type: MemoryOperationType, status: str = "success", member_id: UUID | None = None, source_entity_type: str | None = None, source_entity_id: UUID | None = None) -> None:
        await self._repo.log_memory_operation(
            family_id=family_id,
            operation_type=operation_type,
            status=status,
            member_id=member_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
        )
