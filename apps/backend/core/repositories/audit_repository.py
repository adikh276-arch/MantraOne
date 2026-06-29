from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import AuditLog, MemoryOperation
from core.domain.enums import ActorRole, MemoryOperationType

class AuditRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def log_audit_event(
        self, actor_id: str, action: str, resource: str, result: str, target_id: str | None = None
    ) -> AuditLog:
        log = AuditLog(
            actor_id=actor_id, target_id=target_id, action=action,
            resource=resource, result=result,
        )
        self._db.add(log)
        await self._db.flush()
        return log

    async def log_memory_operation(
        self, family_id: UUID, operation_type: MemoryOperationType, status: str = "success",
        member_id: UUID | None = None, source_entity_type: str | None = None,
        source_entity_id: UUID | None = None, cognee_memory_id: str | None = None,
        error_message: str | None = None, duration_ms: int | None = None,
    ) -> MemoryOperation:
        op = MemoryOperation(
            family_id=family_id, member_id=member_id, operation_type=operation_type.value,
            source_entity_type=source_entity_type, source_entity_id=source_entity_id,
            cognee_memory_id=cognee_memory_id, status=status, error_message=error_message, duration_ms=duration_ms,
        )
        self._db.add(op)
        await self._db.flush()
        return op
