from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from api.dependencies import get_db, get_current_user
from api.permissions import verify_member_access
from infrastructure.database.models import DataGrant

router = APIRouter()


class GrantCreateRequest(BaseModel):
    grantee_id: str
    resource_type: str
    scope: str
    permissions: str
    expires_at: Optional[datetime] = None


class GrantResponse(BaseModel):
    id: str
    grantor_id: str
    grantee_id: str
    resource_type: str
    scope: str
    permissions: str
    expires_at: Optional[datetime]


@router.post("/{member_id}/grants", response_model=GrantResponse)
async def create_grant(
    member_id: UUID,
    request: GrantCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    grant = DataGrant(
        family_id=UUID(user.get("family_id", str(member_id))),
        grantor_id=member_id,
        grantee_id=UUID(request.grantee_id),
        resource_type=request.resource_type,
        scope=request.scope,
        permissions=request.permissions,
        expires_at=request.expires_at,
    )
    db.add(grant)
    await db.commit()
    await db.refresh(grant)
    return {
        "id": str(grant.id),
        "grantor_id": str(grant.grantor_id),
        "grantee_id": str(grant.grantee_id),
        "resource_type": grant.resource_type,
        "scope": grant.scope,
        "permissions": grant.permissions,
        "expires_at": grant.expires_at,
    }


@router.get("/{member_id}/grants", response_model=List[GrantResponse])
async def list_grants(member_id: UUID, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    res = await db.execute(select(DataGrant).where(DataGrant.grantor_id == member_id))
    grants = res.scalars().all()
    return [
        {
            "id": str(g.id),
            "grantor_id": str(g.grantor_id),
            "grantee_id": str(g.grantee_id),
            "resource_type": g.resource_type,
            "scope": g.scope,
            "permissions": g.permissions,
            "expires_at": g.expires_at,
        }
        for g in grants
    ]


@router.delete("/{member_id}/grants/{grant_id}")
async def revoke_grant(
    member_id: UUID, grant_id: UUID, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)
):
    await db.execute(delete(DataGrant).where(DataGrant.id == grant_id, DataGrant.grantor_id == member_id))
    await db.commit()
    return {"status": "success"}
