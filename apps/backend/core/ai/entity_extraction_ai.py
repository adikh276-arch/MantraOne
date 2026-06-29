from pydantic import BaseModel, Field
from typing import List, Optional
from core.ai.registry import registry
from core.ai.session import AISession
from core.ai.prompt_manager import PromptManager


class MedicalEntityList(BaseModel):
    diagnoses: List[str] = []
    medications: List[str] = []
    laboratory_values: List[str] = []
    symptoms: List[str] = []
    procedures: List[str] = []
    vaccinations: List[str] = []
    allergies: List[str] = []
    doctors: List[str] = []
    hospitals: List[str] = []
    recommendations: List[str] = []
    confidence: float = 1.0
    uncertainty: Optional[str] = None


class EntityExtractionAI:
    """
    Extracts structured entities from OCR or conversational text.
    """

    def __init__(self):
        self._prompts = PromptManager()

    async def extract(self, raw_text: str, session: AISession) -> MedicalEntityList:
        provider = registry.get("entity_extraction")

        prompt = self._prompts.load_prompt(
            category="document_extraction", version_file="v1_extract.md", context={"raw_text": raw_text}
        )

        return await provider.generate_structured(
            prompt_text=prompt, response_model=MedicalEntityList, model=session.model
        )
