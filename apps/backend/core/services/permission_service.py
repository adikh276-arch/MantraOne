from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.services.policy_engine import PolicyEngine, PermissionContext, PermissionResult
from core.services.audit_service import AuditService
from infrastructure.database.models import FamilyMember, DataGrant, Document

class PermissionService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._engine = PolicyEngine()
        self._audit = AuditService(db)

    async def verify_access(
        self,
        actor_id: str,
        target_id: str,
        resource_type: str,
        scope: str,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Main entry point for evaluating permissions. Evaluates through PolicyEngine and logs to AuditService.
        """
        # Fetch Actor and Target
        actor_res = await self._db.execute(select(FamilyMember).where(FamilyMember.id == UUID(actor_id)))
        actor = actor_res.scalar_one_or_none()
        
        target_res = await self._db.execute(select(FamilyMember).where(FamilyMember.id == UUID(target_id)))
        target = target_res.scalar_one_or_none()

        if not actor or not target:
            await self._audit.log_audit_event(actor_id, "verify_access", f"{resource_type}:{scope}", "denied - not found", target_id)
            return False

        # Fetch Explicit Grants
        grants_res = await self._db.execute(
            select(DataGrant).where(
                DataGrant.grantee_id == actor.id,
                DataGrant.grantor_id == target.id
            )
        )
        grants = grants_res.scalars().all()
        explicit_grants = [
            {"scope": g.scope, "expires_at": g.expires_at} for g in grants
        ]

        # Check Document Ownership if resource is a document
        is_document_owner = False
        if resource_type == "document" and resource_id:
            doc_res = await self._db.execute(select(Document).where(Document.id == UUID(resource_id)))
            doc = doc_res.scalar_one_or_none()
            if doc and doc.member_id == actor.id:
                is_document_owner = True

        ctx = PermissionContext(
            actor_id=actor.id,
            actor_role=actor.role,
            target_id=target.id,
            target_role=target.role,
            target_relationship=target.relationship,
            resource_type=resource_type,
            resource_id=resource_id,
            scope=scope,
            explicit_grants=explicit_grants,
            is_document_owner=is_document_owner
        )

        result = self._engine.evaluate(ctx)

        # Audit the access attempt
        await self._audit.log_audit_event(
            actor_id=str(actor.id),
            target_id=str(target.id),
            action="verify_access",
            resource=f"{resource_type}:{scope}",
            result="success" if result.is_allowed else f"denied - {result.reason}"
        )

        return result.is_allowed
