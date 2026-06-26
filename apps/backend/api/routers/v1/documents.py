from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from uuid import UUID
from api.dependencies import get_db, get_current_user
from core.services.document_service import DocumentService
from infrastructure.cloud.storage import StorageProvider

router = APIRouter()

@router.post("/")
async def upload_document(
    family_id: UUID = Form(...),
    member_id: UUID = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user)
):
    storage = StorageProvider()
    service = DocumentService(db, storage)
    
    content = await file.read()
    filename = file.filename or "unknown.pdf"
    mime_type = file.content_type or "application/pdf"
    
    doc = await service.initiate_upload(
        content=content,
        filename=filename,
        document_type=document_type,
        member_id=member_id,
        family_id=family_id,
        mime_type=mime_type
    )
    
    processed_doc = await service.process_document(doc, content)
    return {
        "id": processed_doc.id,
        "status": processed_doc.processing_status,
        "memory_ingested": processed_doc.memory_ingested
    }
