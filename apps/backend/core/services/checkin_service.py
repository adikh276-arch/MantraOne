from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.models import DailyCheckin
from core.repositories.checkin_repository import CheckinRepository
from core.repositories.coordinator_decision_repository import CoordinatorDecisionRepository
from core.providers.encryption_service import EncryptionService

class CheckinService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._checkin_repo = CheckinRepository(db)
        self._decision_repo = CoordinatorDecisionRepository(db)
        self._enc = EncryptionService()

    async def submit_checkin(self, coordinator_decision_id: UUID, response_text: str, structured_data: dict, member_id: UUID, family_id: UUID, domain: str) -> DailyCheckin:
        from datetime import datetime, timezone
        decision = await self._decision_repo.get_by_id(coordinator_decision_id, family_id)
        
        checkin = DailyCheckin(
            family_id=family_id,
            member_id=member_id,
            checkin_date=datetime.now(timezone.utc).date(),
            domain=domain,
            raw_response=self._enc.encrypt(response_text),
            structured_data=self._enc.encrypt_json(structured_data),
            coordinator_decision_id=coordinator_decision_id,
            ai_initiated=True,
        )
        saved = await self._checkin_repo.save(checkin)
        
        if decision:
            decision.responded_at = datetime.now(timezone.utc)
            decision.response_id = saved.id
            await self._decision_repo.save(decision)
            
        return saved
