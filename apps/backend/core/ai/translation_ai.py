from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager


class TranslationAI:
    """
    Centralized translation maintaining medical accuracy.
    """

    def __init__(self):
        self._prompts = PromptManager()

    async def translate(self, text: str, target_language: str, session: AISession) -> str:
        provider = registry.get("translation")

        # Optionally use the LLM text generation if the provider doesn't have a native translation endpoint,
        # but the abstract AIProvider has a translate() method.
        # We will use the native method. The SarvamProvider will wrap its MCP translate tool.

        return await provider.translate(text, target_language)
