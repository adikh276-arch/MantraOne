from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from uuid import UUID
from api.dependencies import get_db, get_current_user
from core.services.coordinator_service import CoordinatorService
from core.providers.llm_provider import LLMProvider

router = APIRouter()

@router.get("/daily")
async def get_daily_checkin(family_id: UUID, member_id: UUID, db: AsyncSession = Depends(get_db), user: dict[str, Any] = Depends(get_current_user)):
    # Initialize the LLM provider for the coordinator
    llm = LLMProvider()
    service = CoordinatorService(db, llm)
    
    question = await service.generate_daily_checkin(family_id, member_id)
    return {"question": question}
