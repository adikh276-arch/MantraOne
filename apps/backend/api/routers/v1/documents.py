from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from uuid import UUID
from api.dependencies import get_db, get_current_user
from api.permissions import verify_member_access
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

@router.post("/{document_id}/approve")
async def approve_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user)
    # verify_member_access("document", "write") could be applied here if we resolve member_id from document_id
):
    service = DocumentService(db, StorageProvider())
    doc = await service.approve_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "status": doc.processing_status}

@router.post("/{document_id}/reject")
async def reject_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user)
):
    service = DocumentService(db, StorageProvider())
    doc = await service.reject_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "status": doc.processing_status}
