from __future__ import annotations
import json
from openai import AsyncOpenAI
from pydantic import BaseModel
from config.settings import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog
from core.contracts.llm import ILLMProvider

logger = structlog.get_logger()

class LLMProvider(ILLMProvider):
    COORDINATOR_SYSTEM_PROMPT = """You are MantraOne's gentle health companion..."""
    ESCALATION_SYSTEM_PROMPT = """You are MantraOne's clinical context builder..."""
    NARRATIVE_SYSTEM_PROMPT = """You are MantraOne's health memory builder..."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )
        self._model = settings.groq_model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), reraise=True)
    async def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()

    async def complete_structured(self, system_prompt: str, user_prompt: str, response_schema: type[BaseModel], max_tokens: int = 2000) -> dict:
        text = await self.complete(system_prompt, user_prompt, max_tokens, 0.1)
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0: raise ValueError(f"Invalid JSON: {text[:200]}")
        return json.loads(text[start:end])

    async def generate_checkin_question(self, domain: str, member_name: str, context: str, recent_signals: list[dict]) -> str:
        return await self.complete(self.COORDINATOR_SYSTEM_PROMPT, "Generate question.", 150, 0.7)

    async def generate_escalation_reason(self, domains: list[str], signals: list[dict], member_context: str) -> str:
        return await self.complete(self.ESCALATION_SYSTEM_PROMPT, "Generate escalation.", 300)

    async def build_narrative(self, data_type: str, data_point: dict, member_name: str, baseline_context: str, recent_history: str) -> str:
        return await self.complete(self.NARRATIVE_SYSTEM_PROMPT, "Generate narrative.", 400)
