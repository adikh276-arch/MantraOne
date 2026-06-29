from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from core.repositories.audit_repository import AuditRepository
from core.domain.enums import ActorRole, MemoryOperationType


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = AuditRepository(db)

    async def log_audit_event(
        self, actor_id: str, action: str, resource: str, result: str, target_id: str | None = None
    ) -> None:
        await self._repo.log_audit_event(
            actor_id=actor_id,
            target_id=target_id,
            action=action,
            resource=resource,
            result=result,
        )

    async def log_memory_operation(
        self,
        family_id: UUID,
        operation_type: MemoryOperationType,
        status: str = "success",
        member_id: UUID | None = None,
        source_entity_type: str | None = None,
        source_entity_id: UUID | None = None,
    ) -> None:
        await self._repo.log_memory_operation(
            family_id=family_id,
            operation_type=operation_type,
            status=status,
            member_id=member_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
        )
