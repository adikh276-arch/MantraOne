from uuid import UUID
from datetime import datetime, timezone, timedelta
from core.providers.memory_provider import MemoryProvider
from core.providers.llm_provider import LLMProvider

class MemoryCompressionService:
    """
    Background pipeline that generates Monthly, Quarterly, and Yearly summaries 
    of raw memories. Retrieves prefer summaries to raw facts for high-level queries,
    but never deletes the immutable raw memories.
    """
    
    SYSTEM_PROMPT = """You are a clinical summarization engine. 
    Compress the provided raw medical memories spanning a specific time window into a cohesive,
    lossless summary. Do not omit critical diagnoses, medication changes, or severe alerts.
    Return a structured markdown narrative.
    """

    def __init__(self):
        self._memory = MemoryProvider()
        self._llm = LLMProvider()

    async def compress_period(self, family_id: UUID, member_id: UUID, period: str, start_date: datetime, end_date: datetime) -> None:
        """
        Retrieves all raw memories in a date range and compresses them into a single Summary Node.
        """
        # In a real setup, we would query Cognee for memories exactly matching the date range.
        # Since Cognee is a black box here, we assume a `recall_by_date` function exists.
        
        # fragments = await self._memory.recall_by_date(start_date, end_date, member_id)
        # raw_text = "\n".join([f.content for f in fragments])
        raw_text = "[Simulated raw memories for period]"
        
        prompt = f"Period: {period} ({start_date.date()} to {end_date.date()})\nMemories:\n{raw_text}"
        
        compressed_text = await self._llm.complete(self.SYSTEM_PROMPT, prompt)
        
        # Store the new compressed memory
        await self._memory.remember(
            content=f"[{period.upper()} SUMMARY] {compressed_text}",
            metadata={
                "family_id": family_id,
                "member_id": member_id,
                "memory_type": "compressed_summary",
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        )
