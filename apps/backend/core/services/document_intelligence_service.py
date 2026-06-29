from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.database.models import Document, Diagnosis, Medication
from core.providers.llm_provider import LLMProvider
import structlog

logger = structlog.get_logger()

class ExtractedEntity(BaseModel):
    name: str
    type: str  # e.g., 'diagnosis', 'medication', 'lab_result'
    confidence: float

class DocumentExtractionResult(BaseModel):
    document_type: str = Field(description="e.g., lab_report, prescription, discharge_summary, invoice")
    document_date: Optional[date] = Field(None, description="The primary date the document was issued or relates to, in YYYY-MM-DD format")
    confidence: float = Field(..., description="Overall confidence score of this extraction between 0.0 and 1.0")
    member_name: Optional[str] = Field(None, description="Name of the patient mentioned")
    provider: Optional[str] = Field(None, description="Issuing doctor, hospital, or lab name")
    summary: str = Field(..., description="A 1-2 sentence summary of the document")
    entities: List[ExtractedEntity] = Field(default_factory=list, description="Key medical entities found")

class DocumentIntelligenceService:
    SYSTEM_PROMPT = """You are a highly accurate clinical document extraction engine.
    Extract the requested information from the provided raw OCR text.
    Return ONLY a valid JSON object matching the exact structure requested, with no markdown formatting.
    """

    def __init__(self, db: AsyncSession):
        self._db = db
        self._llm = LLMProvider()

    async def check_exact_duplicate(self, checksum: str) -> Optional[UUID]:
        """Returns the ID of an exact byte-for-byte duplicate if one exists."""
        res = await self._db.execute(select(Document).where(Document.checksum_sha256 == checksum))
        doc = res.scalars().first()
        return doc.id if doc else None

    async def extract_metadata(self, text: str) -> DocumentExtractionResult:
        """Extracts structured metadata from document text using the LLM."""
        prompt = f"Extract metadata from this document text:\n\n{text[:8000]}" # Truncate to save context if huge
        
        # We need to construct a JSON schema guide for the LLM since the provider doesn't strictly enforce it
        # However, the prompt can just say "Return JSON matching..."
        prompt += """\n\nReturn JSON matching exactly this schema:
{
  "document_type": "string",
  "document_date": "YYYY-MM-DD",
  "confidence": 0.95,
  "member_name": "string",
  "provider": "string",
  "summary": "string",
  "entities": [
    {"name": "string", "type": "string", "confidence": 0.9}
  ]
}"""
        try:
            raw_dict = await self._llm.complete_structured(
                self.SYSTEM_PROMPT,
                prompt,
                response_schema=DocumentExtractionResult,
                max_tokens=1500
            )
            return DocumentExtractionResult(**raw_dict)
        except Exception as e:
            logger.error("metadata_extraction_failed", error=str(e))
            # Fallback
            return DocumentExtractionResult(
                document_type="unknown",
                confidence=0.0,
                summary="Failed to extract metadata."
            )

    async def determine_semantic_duplicate(self, extracted: DocumentExtractionResult, member_id: UUID) -> tuple[Optional[UUID], float]:
        """
        Determines if there is a semantic duplicate by comparing date, provider, diagnosis, and medications.
        Returns a tuple of (duplicate_doc_id, similarity_score).
        """
        if not extracted.document_date:
            return None, 0.0

        # Find existing docs with same member and date (and maybe type)
        # Using a wide net for dates +/- a few days might be better, but exact match is a good start.
        res = await self._db.execute(
            select(Document)
            .where(
                Document.member_id == member_id,
                Document.document_date == extracted.document_date
            )
        )
        candidates = res.scalars().all()
        if not candidates:
            return None, 0.0

        best_match_id = None
        highest_score = 0.0

        for candidate in candidates:
            score = 0.0
            
            # Same date (already filtered, so +0.4)
            score += 0.4
            
            # Same type?
            if candidate.document_type == extracted.document_type:
                score += 0.2
                
            # Same provider?
            if candidate.issued_by and extracted.provider and candidate.issued_by.lower() == extracted.provider.lower():
                score += 0.2
                
            # Compare entities (diagnoses, meds) if structured_data exists
            # We'll do a simple overlap check of entity names.
            if candidate.structured_data:
                import json
                try:
                    c_data = json.loads(candidate.structured_data)
                    c_entities = [e.get("name", "").lower() for e in c_data.get("entities", [])]
                    e_entities = [e.name.lower() for e in extracted.entities]
                    
                    overlap = set(c_entities).intersection(set(e_entities))
                    if overlap:
                        score += 0.2 * (len(overlap) / max(len(c_entities), 1))
                except Exception:
                    pass

            if score > highest_score:
                highest_score = score
                best_match_id = candidate.id

        return best_match_id, highest_score

    async def evaluate_document(self, doc: Document, text: str) -> None:
        """
        Orchestrates the intelligence pipeline for a document:
        1. Extract metadata
        2. Check semantic duplicates
        3. Route to proper review status
        """
        extracted = await self.extract_metadata(text)
        
        doc.document_date = extracted.document_date
        doc.document_date_confidence = extracted.confidence
        doc.issued_by = extracted.provider
        doc.document_type = extracted.document_type
        doc.structured_data = extracted.model_dump_json()

        # Route
        if extracted.confidence < 0.8:
            doc.processing_status = "needs_review"
            return

        duplicate_id, similarity = await self.determine_semantic_duplicate(extracted, doc.member_id)
        
        if similarity >= 0.8:
            doc.duplicate_of_id = duplicate_id
            doc.processing_status = "needs_review"
            logger.info("semantic_duplicate_flagged", doc_id=doc.id, duplicate_of=duplicate_id, score=similarity)
        else:
            # High confidence, no semantic duplicate
            doc.processing_status = "approved" # Can go straight to ingestion
