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
        # We need a memory provider to ingest documents
        from core.providers.memory_provider import MemoryProvider
        self._memory = MemoryProvider()

    async def initiate_upload(self, content: bytes, filename: str, document_type: str, member_id: UUID, family_id: UUID, mime_type: str) -> Document:
        import uuid
        file_uuid = uuid.uuid4()
        extension = filename.split('.')[-1] if '.' in filename else ''
        
        gcs_path = await self._storage.upload(
            content=content,
            family_id=family_id,
            member_id=member_id,
            document_type=document_type,
            file_uuid=file_uuid,
            extension=extension,
        )
        
        checksum = self._storage.compute_checksum(content)  # type: ignore
        
        doc = Document(
            family_id=family_id,
            member_id=member_id,
            document_type=document_type,
            original_filename=self._enc.encrypt(filename),
            gcs_path=gcs_path,
            mime_type=mime_type,
            file_size_bytes=len(content),
            checksum_sha256=checksum,
        )
        return await self._repo.save(doc)

    async def process_document(self, doc: Document, content: bytes) -> Document:
        import pdfplumber
        import io
        from core.domain.entities import HealthMemoryMetadata
        from datetime import datetime
        
        extracted_text = ""
        if doc.mime_type == "application/pdf":
            try:
                with pdfplumber.open(io.BytesIO(content)) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages]
                    extracted_text = "\n".join(pages)
            except Exception as e:
                doc.processing_status = "failed"
                doc.error_message = f"PDF extraction failed: {str(e)}"
                return await self._repo.save(doc)
        else:
            doc.processing_status = "failed"
            doc.error_message = "Unsupported mime type for extraction"
            return await self._repo.save(doc)

        if not extracted_text.strip():
            doc.processing_status = "failed"
            doc.error_message = "No text extracted from document"
            return await self._repo.save(doc)

        doc.extracted_text = extracted_text
        doc.processing_status = "processed"

        # Ingest to Memory
        metadata = HealthMemoryMetadata(
            family_id=doc.family_id,
            member_id=doc.member_id,
            source_type="document",
            source_id=doc.id,
            timestamp=datetime.now()
        )
        try:
            memory_id = await self._memory.remember(content=extracted_text, metadata=metadata)
            doc.memory_ingested = True
            doc.memory_ingested_at = datetime.now()
        except Exception as e:
            doc.error_message = f"Memory ingestion failed: {str(e)}"
            
        return await self._repo.save(doc)
