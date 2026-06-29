from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from pydantic import BaseModel
from uuid import UUID

from api.dependencies import get_db, get_current_user
from core.services.outcome_learning_service import OutcomeLearningService

router = APIRouter()


class ClinicalOutcomePayload(BaseModel):
    member_id: str
    diagnosis: str
    treatment_plan: str
    doctor_notes: str


@router.post("/outcomes", status_code=201)
async def submit_clinical_outcome(
    payload: ClinicalOutcomePayload,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
):
    """
    Ingests outcomes from clinical consultations and feeds them back into the system
    as high-confidence ground truth memories.
    """
    family_id_str = user.get("family_id")
    if not family_id_str:
        raise HTTPException(status_code=401, detail="Family ID missing from token")

    outcome_service = OutcomeLearningService(db)

    await outcome_service.ingest_outcome(
        family_id=UUID(family_id_str),
        member_id=UUID(payload.member_id),
        diagnosis=payload.diagnosis,
        treatment_plan=payload.treatment_plan,
        notes=payload.doctor_notes,
    )

    return {"status": "success", "message": "Clinical outcome ingested and memory updated."}
