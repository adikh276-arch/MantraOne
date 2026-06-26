from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from uuid import UUID
from pydantic import BaseModel
from api.dependencies import get_db, get_current_user
from core.services.health_record_service import HealthRecordService
from core.events.publisher import EventPublisher
from infrastructure.events.redis_bus import RedisEventBus

router = APIRouter()

class MetricRequest(BaseModel):
    family_id: UUID
    member_id: UUID
    metric_type: str
    value: float
    source: str = "manual"

@router.post("/metrics")
async def record_metric(req: MetricRequest, db: AsyncSession = Depends(get_db), user: dict[str, Any] = Depends(get_current_user)):
    # Initialize the redis bus
    import os
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    bus = RedisEventBus(redis_url)
    publisher = EventPublisher(bus)
    service = HealthRecordService(db, publisher)
    
    metric = await service.record_metric(
        family_id=req.family_id,
        member_id=req.member_id,
        metric_type=req.metric_type,
        value=req.value,
        source=req.source
    )
    return {"id": metric.id}
