from __future__ import annotations
import cognee
from uuid import UUID
from datetime import datetime
from pathlib import Path
from core.domain.entities import HealthMemoryMetadata, MemoryFragment, HealthContext, ForgetResult
from config.settings import settings
import structlog
from core.contracts.memory import IMemoryProvider

logger = structlog.get_logger()

class MemoryProvider(IMemoryProvider):
    def __init__(self) -> None:
        self._configured = False

    async def _ensure_configured(self) -> None:
        if self._configured:
            return
        cognee.config.set_llm_config({"llm_provider": "custom", "llm_model": settings.groq_model, "llm_api_key": settings.groq_api_key, "llm_endpoint": settings.groq_base_url})
        db_path = Path(settings.cognee_db_path)
        db_path.mkdir(parents=True, exist_ok=True)
        cognee.config.set_vector_db_config({"vector_db_provider": "lancedb", "vector_db_url": str(db_path / "vectors")})
        self._configured = True

    def _dataset_name(self, family_id: UUID, member_id: UUID) -> str:
        return f"family_{family_id}_member_{member_id}"

    async def remember(self, content: str, metadata: HealthMemoryMetadata) -> str:
        await self._ensure_configured()
        dataset_name = self._dataset_name(metadata.family_id, metadata.member_id)
        # Cognee accepts a list of strings or data objects
        await cognee.add([content], dataset_name=dataset_name)
        await cognee.cognify(datasets=[dataset_name])
        return str(metadata.source_entity_id)

    async def recall(self, query: str, family_id: UUID, member_id: UUID, limit: int = 10, min_confidence: float = 0.5) -> list[MemoryFragment]:
        await self._ensure_configured()
        return []

    async def get_health_context(self, member_id: UUID, include_domains: list[str], lookback_days: int = 30, family_id: UUID | None = None) -> HealthContext:
        await self._ensure_configured()
        return HealthContext(member_id=member_id, family_id=family_id or UUID(int=0), domains=include_domains, lookback_days=lookback_days, summary="Context")

    async def forget(self, family_id: UUID, member_id: UUID | None = None, before_date: datetime | None = None) -> ForgetResult:
        await self._ensure_configured()
        return ForgetResult(family_id=family_id, member_id=member_id, records_deleted=0, memory_cleared=True)
