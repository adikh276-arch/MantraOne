from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from infrastructure.database.models import Document
from core.repositories.document_repository import DocumentRepository
from core.providers.encryption_service import EncryptionService


class DocumentService:
    def __init__(self, db: AsyncSession, storage_provider: Any) -> None:
        self._db = db
        self._repo = DocumentRepository(db)
        self._enc = EncryptionService()
        self._storage = storage_provider

        from core.providers.memory_provider import MemoryProvider

        self._memory = MemoryProvider()

        from core.services.document_intelligence_service import DocumentIntelligenceService

        self._intelligence = DocumentIntelligenceService(db)

    async def initiate_upload(
        self, content: bytes, filename: str, document_type: str, member_id: UUID, family_id: UUID, mime_type: str
    ) -> Document:
        import hashlib

        checksum = hashlib.sha256(content).hexdigest()

        # Check exact duplicate
        duplicate_id = await self._intelligence.check_exact_duplicate(checksum)
        if duplicate_id:
            raise ValueError(f"Exact duplicate found: {duplicate_id}")

        import uuid

        file_uuid = uuid.uuid4()
        extension = filename.split(".")[-1] if "." in filename else ""

        gcs_path = await self._storage.upload(
            content=content,
            family_id=family_id,
            member_id=member_id,
            document_type=document_type,
            file_uuid=file_uuid,
            extension=extension,
        )

        import hashlib

        checksum = hashlib.sha256(content).hexdigest()

        doc = Document(
            family_id=family_id,
            member_id=member_id,
            document_type=document_type,
            original_filename=self._enc.encrypt(filename),
            gcs_path=gcs_path,
            mime_type=mime_type,
            file_size_bytes=len(content),
            checksum_sha256=checksum,
            processing_status="processing",
        )
        return await self._repo.save(doc)

    async def process_document(self, doc: Document, content: bytes) -> Document:
        import pdfplumber
        import io
        from core.domain.entities import HealthMemoryMetadata, MemoryType
        from datetime import datetime
        import structlog

        logger = structlog.get_logger()

        extracted_text = ""
        if doc.mime_type == "application/pdf":
            try:
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages]
                    extracted_text = "\n".join(pages)
            except Exception as e:
                logger.error("pdf_extraction_failed", error=str(e), document_id=doc.id)
                doc.processing_status = "failed"
                return await self._repo.save(doc)
        else:
            logger.error("unsupported_mime_type", mime_type=doc.mime_type, document_id=doc.id)
            doc.processing_status = "failed"
            return await self._repo.save(doc)

        if not extracted_text.strip():
            logger.error("no_text_extracted", document_id=doc.id)
            doc.processing_status = "failed"
            return await self._repo.save(doc)

        doc.extracted_text = extracted_text

        # Delegate intelligence (LLM extraction, semantic duplicate checking, routing)
        await self._intelligence.evaluate_document(doc, extracted_text)

        # If it was approved (high confidence, no semantic duplicates), ingest memory immediately.
        if doc.processing_status == "approved":
            metadata = HealthMemoryMetadata(
                family_id=doc.family_id,
                member_id=doc.member_id,
                memory_type=MemoryType.DOCUMENT,
                source_entity_type="document",
                source_entity_id=doc.id,
                timestamp=datetime.now(),
            )
            try:
                await self._memory.remember(content=extracted_text, metadata=metadata)
                doc.memory_ingested = True
                doc.memory_ingested_at = datetime.now()
                doc.processing_status = "ingested"
            except Exception as e:
                logger.error("memory_ingestion_failed", error=str(e), document_id=doc.id)
                doc.processing_status = "needs_review"  # Need manual intervention or retry

        return await self._repo.save(doc)

    async def approve_document(self, document_id: UUID) -> Optional[Document]:
        import structlog
        from datetime import datetime
        from core.domain.entities import HealthMemoryMetadata, MemoryType

        logger = structlog.get_logger()

        doc = await self._repo.get_by_id(document_id)
        if not doc or doc.processing_status != "needs_review":
            return doc

        doc.processing_status = "approved"

        # Ingest to Memory
        if doc.extracted_text and not doc.memory_ingested:
            metadata = HealthMemoryMetadata(
                family_id=doc.family_id,
                member_id=doc.member_id,
                memory_type=MemoryType.DOCUMENT,
                source_entity_type="document",
                source_entity_id=doc.id,
                timestamp=datetime.now(),
            )
            try:
                await self._memory.remember(content=doc.extracted_text, metadata=metadata)
                doc.memory_ingested = True
                doc.memory_ingested_at = datetime.now()
                doc.processing_status = "ingested"

                # Publish MEMORY_UPDATED event for Intelligence Pipeline
                from infrastructure.cache.redis_client import get_redis_client
                from core.events.publisher import EventPublisher
                import json

                redis = await get_redis_client()
                publisher = EventPublisher(redis)

                # We need the extracted entities for FollowUpService
                entities = []
                if doc.structured_data:
                    try:
                        data = json.loads(doc.structured_data)
                        entities = data.get("entities", [])
                    except Exception:
                        pass

                payload = {
                    "family_id": str(doc.family_id),
                    "member_id": str(doc.member_id),
                    "new_data_text": doc.extracted_text,
                    "entities": entities,
                    "memory_type": "document",
                }
                # Since we don't have ARQ setup immediately wired, we will publish the event.
                # The intelligence_worker task would listen to this event.
                await publisher.publish("MEMORY_UPDATED", payload)

            except Exception as e:
                logger.error("memory_ingestion_failed_on_approval", error=str(e), document_id=doc.id)
                # Keep it approved so it can be retried, or set to failed

        return await self._repo.save(doc)

    async def reject_document(self, document_id: UUID) -> Optional[Document]:
        doc = await self._repo.get_by_id(document_id)
        if not doc or doc.processing_status != "needs_review":
            return doc

        doc.processing_status = "rejected"
        return await self._repo.save(doc)
