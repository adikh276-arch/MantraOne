from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from api.dependencies import get_db, get_current_user
from core.services.health_graph_projection_service import HealthGraphProjectionService

router = APIRouter()


@router.get("/graph")
async def get_memory_graph(family_id: UUID, db: AsyncSession = Depends(get_db)):
    service = HealthGraphProjectionService(db)
    graph = await service.get_family_graph(family_id)
    return graph
