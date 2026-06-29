from core.ai.session import AISession
from core.ai.ocr_ai import OCRAI
from core.ai.entity_extraction_ai import EntityExtractionAI, MedicalEntityList


class DocumentAI:
    """
    Coordinates the OCR pipeline from raw document to structured medical entities.
    """

    def __init__(self):
        self._ocr = OCRAI()
        self._extractor = EntityExtractionAI()

    async def process_document(self, file_path: str, session: AISession) -> MedicalEntityList:
        # 1. OCR
        raw_text = await self._ocr.extract_text(file_path, session)

        # 2. Structure Extraction
        entities = await self._extractor.extract(raw_text, session)

        return entities
