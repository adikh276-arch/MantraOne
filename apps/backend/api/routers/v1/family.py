from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from uuid import UUID

from api.dependencies import get_db, get_current_user
from core.services.family_digital_twin_service import FamilyDigitalTwinService
from core.domain.entities import FamilyDigitalTwin

router = APIRouter()

@router.get("/summary", response_model=FamilyDigitalTwin)
async def get_family_summary(
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user)
):
    """
    Returns the comprehensive Family Digital Twin containing current attention items,
    recent changes, active conditions, pending follow-ups, missing information, and insights.
    This serves as the primary data source for the frontend executive briefing homepage.
    """
    family_id_str = user.get("family_id")
    member_id_str = user.get("member_id") # We keep this for auth structure, but twin is family-wide
    
    if not family_id_str:
        raise HTTPException(status_code=401, detail="Family ID missing from token")
        
    family_id = UUID(str(family_id_str))
    
    twin_service = FamilyDigitalTwinService(db)
    twin = await twin_service.get_digital_twin(family_id)
    
    return twin
