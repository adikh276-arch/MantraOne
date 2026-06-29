from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from api.dependencies import get_db, get_current_user
from core.services.timeline_service import TimelineService

router = APIRouter()


@router.get("/")
async def get_family_timeline(family_id: UUID, db: AsyncSession = Depends(get_db)):
    service = TimelineService(db)
    events = await service.build_timeline(family_id)
    return {"events": events}
