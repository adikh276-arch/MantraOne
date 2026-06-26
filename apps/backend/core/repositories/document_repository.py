from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from infrastructure.database.models import Document
from core.repositories.base import BaseRepository

class DocumentRepository(BaseRepository[Document]):
    model = Document

    async def list_for_member(self, member_id: UUID, family_id: UUID, document_type: str | None = None, limit: int = 50) -> list[Document]:
        conditions = [
            Document.member_id == member_id,
            Document.family_id == family_id,
            Document.deleted_at.is_(None),
        ]
        if document_type:
            conditions.append(Document.document_type == document_type)
        result = await self._db.execute(
            select(Document).where(*conditions)
            .order_by(Document.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_processing(self, limit: int = 10) -> list[Document]:
        result = await self._db.execute(
            select(Document).where(
                Document.processing_status.in_(["pending", "processing"]),
                Document.deleted_at.is_(None),
            ).order_by(Document.created_at).limit(limit)
        )
        return list(result.scalars().all())
