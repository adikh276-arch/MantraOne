from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager


class ReasoningAI:
    """
    Translates deterministic system decisions into reassuring explanations for the user.
    """

    def __init__(self):
        self._prompts = PromptManager()

    async def explain_decision(self, decision_type: str, reasoning_inputs: dict, session: AISession) -> str:
        provider = registry.get("reasoning")

        prompt = self._prompts.load_prompt(
            category="clinical_reasoning",
            version_file="v1_explain.md",
            context={"decision_type": decision_type, "reasoning_inputs": str(reasoning_inputs)},
        )

        return await provider.generate_text(prompt_text=prompt, model=session.model)
