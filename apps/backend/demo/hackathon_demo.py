import asyncio
import json
import uuid
import structlog
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config.settings import settings
from infrastructure.database.session import Base
from infrastructure.database.models import Family, FamilyMember
from core.services.document_service import DocumentService
from core.services.health_record_service import HealthRecordService
from core.events.publisher import EventPublisher
from infrastructure.cache.redis_client import get_redis_pool
from redis.asyncio import Redis

logger = structlog.get_logger()

# Setup Local DB and Redis
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class MockStorageProvider:
    async def upload(self, **kwargs) -> str:
        return f"/mock/gcs/path/{kwargs.get('filename', 'doc.pdf')}"

    def compute_checksum(self, content: bytes) -> str:
        return "mock_sha256"


async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("    -> Database schema recreated.")


async def run_demo():
    print("=" * 60)
    print("🚀 MANTRAONE HACKATHON DEMO 🚀")
    print("=" * 60)

    # 1. Setup & Reset
    print("\n[1] Initializing Database & Services...")
    await setup_db()

    redis_pool = get_redis_pool()
    redis_client = Redis(connection_pool=redis_pool)
    event_publisher = EventPublisher(redis_client)

    # Load sample family data
    with open("demo/sample_family.json", "r") as f:
        family_data = json.load(f)["family"]

    async with AsyncSessionLocal() as db:
        # Create Family
        family = Family(
            id=uuid.uuid4(), name=family_data["name"], primary_user_id="mock_firebase_uid", subscription_tier="premium"
        )
        db.add(family)

        # Create Primary Member (Dad)
        dad = FamilyMember(
            id=uuid.uuid4(),
            family_id=family.id,
            name=family_data["primary_user"]["name"],
            relationship=family_data["primary_user"]["relationship"],
            date_of_birth=family_data["primary_user"]["date_of_birth"],
            timezone=family_data["primary_user"]["timezone"],
            is_primary=True,
        )
        db.add(dad)
        await db.commit()
        await db.refresh(family)
        await db.refresh(dad)
        print(f"    -> Created Family: {family.name} | Primary: {dad.name}")

    print("\n[2] Scenario 1: Document Ingestion (The Memory Loop)")
    with open("demo/sample_prescription.pdf", "rb") as f:
        pdf_bytes = f.read()
    print(f"    -> Uploading 'sample_prescription.pdf' ({len(pdf_bytes)} bytes)")

    async with AsyncSessionLocal() as db:
        doc_service = DocumentService(db, storage_provider=MockStorageProvider())
        doc = await doc_service.initiate_upload(
            content=pdf_bytes,
            filename="sample_prescription.pdf",
            document_type="prescription",
            member_id=dad.id,
            family_id=family.id,
            mime_type="application/pdf",
        )
        print("    -> Processing document and extracting text...")
        processed_doc = await doc_service.process_document(doc, pdf_bytes)
        if processed_doc.processing_status == "failed":
            print(f"    -> [ERROR] {processed_doc.error_message}")
        else:
            print(f"    -> [SUCCESS] Text extracted & Ingested to Memory (ID: {doc.id})")
            print(f"    -> Extracted preview: {processed_doc.extracted_text[:100]}...")

    print("\n[3] Scenario 2: Watchers & The Event Bus")
    print("    -> Dad sleeps poorly for 3 days...")
    async with AsyncSessionLocal() as db:
        hr_service = HealthRecordService(db, event_publisher=event_publisher)
        for i in range(3):
            await hr_service.record_metric(
                member_id=dad.id,
                family_id=family.id,
                metric_type="sleep_duration",
                recorded_at=datetime.now(timezone.utc) - timedelta(days=i),
                value_numeric=4.0,  # 4 hours of sleep
                unit="hours",
            )
        print("    -> Sleep metrics recorded and events published!")

        from core.workers.watchers.sleep_watcher import SleepWatcher
        from core.events.types import HealthMetricRecordedEvent

        sleep_event = HealthMetricRecordedEvent(
            metric_id=uuid.uuid4(),
            family_id=family.id,
            member_id=dad.id,
            metric_type="sleep_duration",
            value=4.0,
            recorded_at=datetime.now(timezone.utc),
        )

        watcher = SleepWatcher()
        print("    -> Evaluating Watcher constraints...")
        # Note: in Python 3.12, if _process returns a signal we capture it:
        signal = await watcher._process(str(dad.id), str(family.id), [sleep_event])
        if signal:
            print(f"    -> [SUCCESS] SleepWatcher generated HIGH severity signal: {signal.signal_payload}")
        else:
            print("    -> [WARNING] No signal generated!")

    print("\n[4] Scenario 3: The Coordinator Engine")
    print("    -> Watcher signals Coordinator...")
    async with AsyncSessionLocal() as db:
        from core.repositories.watcher_signal_repository import WatcherSignalRepository
        from core.services.coordinator_service import CoordinatorService

        signal.family_id = family.id
        signal.member_id = dad.id
        signal_repo = WatcherSignalRepository(db)
        await signal_repo.save(signal)

        coord_service = CoordinatorService(db)
        decision = await coord_service.select_daily_signal(dad.id, family.id)
        if decision:
            print(f"    -> [SUCCESS] Coordinator selected domain: {decision.selected_domain.value}")
            print(f"    -> AI Generated Question: '{decision.checkin_generated}'")
        else:
            print("    -> [WARNING] Coordinator made no decision.")

    print("\n[5] Scenario 4: Escalation & Consultation")
    print("    -> Multiple risk factors intersect (Poor Sleep + Stress)...")
    async with AsyncSessionLocal() as db:
        from core.domain.enums import WatcherDomain, SignalType, SignalSeverity, TrendDirection
        from core.domain.entities import WatcherSignalEntity

        stress_signal = WatcherSignalEntity(
            id=uuid.uuid4(),
            family_id=family.id,
            member_id=dad.id,
            watcher_domain=WatcherDomain.STRESS,
            signal_date=datetime.now(timezone.utc).date(),
            signal_type=SignalType.ANOMALY,
            severity=SignalSeverity.MEDIUM,
            signal_payload={"stress_level": "high"},
            deviation_from_baseline=1.5,
            trend_direction=TrendDirection.WORSENING,
            supporting_data={},
            surfaced=False,
            expires_at=None,
            created_at=datetime.now(timezone.utc),
        )
        await signal_repo.save(stress_signal)

        from core.services.escalation_service import EscalationService

        esc_service = EscalationService(db)
        print("    -> Evaluating Escalation thresholds...")
        event = await esc_service.evaluate_escalation(dad.id, family.id)
        if event:
            print(f"    -> [SUCCESS] Escalation Triggered! Specialty: {event.recommended_specialty}")
            print(f"    -> Doctor Consultation Brief:\n{event.escalation_reason}")
        else:
            print("    -> [WARNING] Escalation not triggered.")

    print("\n[6] Scenario 5: Typed Memory Retrieval")
    print("    -> Validating AI Memory: 'What medicines has Dad stopped?'...")
    async with AsyncSessionLocal() as db:
        from core.providers.memory_provider import MemoryProvider

        memory = MemoryProvider()

        # We can simulate the typed recall!
        fragments = await memory.recall("medicines stopped", dad.id, family.id)
        if fragments:
            print(f"    -> [SUCCESS] Recalled {len(fragments)} memory fragments!")
            for frag in fragments:
                print(f"       - '{frag.content}' (Score: {frag.score})")
        else:
            print("    -> [WARNING] No fragments recalled.")

    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
