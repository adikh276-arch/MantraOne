from __future__ import annotations
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.database.models import Document, WatcherSignal, DailyCheckin


class TimelineService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def build_timeline(self, family_id: UUID) -> list[dict]:
        events = []

        # 1. Documents (Labs, Reports)
        docs = await self._db.execute(select(Document).where(Document.family_id == family_id))
        for doc in docs.scalars().all():
            events.append(
                {
                    "id": str(doc.id),
                    "timestamp": doc.created_at.isoformat(),
                    "type": "document",
                    "title": f"Uploaded {doc.document_type}",
                    "description": doc.original_filename or f"Document size: {doc.file_size_bytes} bytes",
                    "badge": "Document Ingestion",
                    "severity": "info",
                }
            )

        # 2. Watcher Signals (Alerts, Anomalies)
        signals = await self._db.execute(select(WatcherSignal).where(WatcherSignal.family_id == family_id))
        for signal in signals.scalars().all():
            events.append(
                {
                    "id": str(signal.id),
                    "timestamp": signal.created_at.isoformat(),
                    "type": "signal",
                    "title": f"{signal.watcher_domain.capitalize()} Signal",
                    "description": str(signal.signal_payload),
                    "badge": f"{signal.severity.capitalize()} Priority",
                    "severity": signal.severity,
                }
            )

        # 3. Check-ins
        checkins = await self._db.execute(select(DailyCheckin).where(DailyCheckin.family_id == family_id))
        for checkin in checkins.scalars().all():
            events.append(
                {
                    "id": str(checkin.id),
                    "timestamp": checkin.created_at.isoformat(),
                    "type": "checkin",
                    "title": f"Daily Check-in ({checkin.domain})",
                    "description": checkin.raw_response or "Completed structured check-in",
                    "badge": "Routine Check-in",
                    "severity": "info",
                }
            )

        # Sort by timestamp descending
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        return events
