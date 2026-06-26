from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import AuditLog, MemoryOperation
from core.domain.enums import ActorRole, MemoryOperationType

class AuditRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def log_phi_access(
        self, actor_firebase_uid: str, actor_role: ActorRole, action: str,
        resource_type: str, result: str, family_id: UUID | None = None,
        member_id: UUID | None = None, resource_id: UUID | None = None,
        endpoint: str | None = None, ip_address: str | None = None, user_agent: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            family_id=family_id, member_id=member_id, actor_firebase_uid=actor_firebase_uid,
            actor_role=actor_role.value, action=action, resource_type=resource_type,
            resource_id=resource_id, endpoint=endpoint, ip_address=ip_address,
            user_agent=user_agent, result=result,
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
