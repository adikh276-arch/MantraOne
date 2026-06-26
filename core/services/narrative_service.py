from __future__ import annotations
from core.providers.llm_provider import LLMProvider

class NarrativeService:
    def __init__(self) -> None:
        self._llm = LLMProvider()

    async def build_checkin_narrative(self, checkin: dict, member_name: str, baseline: str) -> str:
        return await self._llm.build_narrative(
            data_type="daily_checkin",
            data_point=checkin,
            member_name=member_name,
            baseline_context=baseline,
            recent_history="",
        )

    async def build_metric_narrative(self, metric: dict, member_name: str, baseline: str) -> str:
        return await self._llm.build_narrative(
            data_type="health_metric",
            data_point=metric,
            member_name=member_name,
            baseline_context=baseline,
            recent_history="",
        )
