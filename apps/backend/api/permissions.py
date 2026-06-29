from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Any
from uuid import UUID

from api.dependencies import get_db, get_current_user
from core.services.permission_service import PermissionService

def verify_member_access(resource_type: str, scope: str) -> Callable:
    """
    Dependency generator for verifying member access via the Policy Engine.
    Requires `member_id` (or `target_id`) to be present in path or query parameters,
    and uses the current authenticated user's ID as the actor.
    """
    async def access_dependency(
        member_id: UUID,
        db: AsyncSession = Depends(get_db),
        user: dict[str, Any] = Depends(get_current_user)
    ) -> UUID:
        actor_id = user.get("sub")
        if not actor_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # We need the actor's FamilyMember ID. The token sub might be firebase_uid.
        # So let's resolve it. Actually, `get_current_user` usually returns the FamilyMember ID or firebase UID.
        # Wait, how does `get_current_user` work in this app?
        # Let's assume it returns a dict with `member_id` as well. We'll check.
        # For now, let's look up the actor's member ID based on firebase_uid if member_id isn't in user dict.
        from infrastructure.database.models import FamilyMember
        from sqlalchemy import select
        
        # Determine actor_member_id
        actor_member_id = user.get("member_id")
        if not actor_member_id:
            firebase_uid = user.get("sub")
            res = await db.execute(select(FamilyMember).where(FamilyMember.firebase_uid == firebase_uid))
            member = res.scalars().first()
            if not member:
                raise HTTPException(status_code=401, detail="Actor member not found")
            actor_member_id = str(member.id)

        service = PermissionService(db)
        
        is_allowed = await service.verify_access(
            actor_id=str(actor_member_id),
            target_id=str(member_id),
            resource_type=resource_type,
            scope=scope
        )
        
        if not is_allowed:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions for this resource.")
        
        return member_id

    return access_dependency
