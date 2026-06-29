from abc import ABC, abstractmethod
from pydantic import BaseModel


class ILLMProvider(ABC):
    @abstractmethod
    async def complete(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1000, temperature: float = 0.3
    ) -> str:
        pass

    @abstractmethod
    async def complete_structured(
        self, system_prompt: str, user_prompt: str, response_schema: type[BaseModel], max_tokens: int = 2000
    ) -> dict:
        pass

    @abstractmethod
    async def generate_checkin_question(
        self, domain: str, member_name: str, context: str, recent_signals: list[dict]
    ) -> str:
        pass

    @abstractmethod
    async def generate_escalation_reason(self, domains: list[str], signals: list[dict], member_context: str) -> str:
        pass

    @abstractmethod
    async def build_narrative(
        self, data_type: str, data_point: dict, member_name: str, baseline_context: str, recent_history: str
    ) -> str:
        pass
