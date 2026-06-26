from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from infrastructure.database.models import Document
from core.repositories.document_repository import DocumentRepository
from core.providers.encryption_service import EncryptionService
from infrastructure.cloud.storage import StorageProvider

class DocumentService:
    def __init__(self, db: AsyncSession, storage_provider: Any) -> None:
        self._db = db
        self._repo = DocumentRepository(db)
        self._enc = EncryptionService()
        self._storage = storage_provider

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
