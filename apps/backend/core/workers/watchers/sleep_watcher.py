from core.workers.watchers.base_watcher import BaseWatcher
from core.events.types import BaseHealthEvent
from core.domain.enums import WatcherDomain
from core.domain.entities import WatcherSignalEntity


class SleepWatcher(BaseWatcher):
    domain = WatcherDomain.SLEEP

    async def _process(
        self, member_id: str, family_id: str, events: list[BaseHealthEvent]
    ) -> WatcherSignalEntity | None:
        from core.domain.enums import SignalType, SignalSeverity, TrendDirection
        from datetime import datetime, timezone
        from uuid import uuid4
        import structlog

        logger = structlog.get_logger()

        # In a real watcher, we would fetch historical metrics from repository
        # For scenario driven demo, we examine the current events
        sleep_events = [e for e in events if getattr(e, "metric_type", "") == "sleep_duration"]
        if not sleep_events:
            return None

        recent_sleep = sleep_events[-1]
        value = getattr(recent_sleep, "value", 0.0)

        if value < 5.0:
            logger.warning("sleep_watcher_triggered", member_id=member_id, value=value)
            # Create a signal! We will store it in DB using WatcherSignalRepository in a real app.
            # But we can also publish it directly back to the Event Bus for the Coordinator!
            signal = WatcherSignalEntity(
                id=uuid4(),
                family_id=uuid4(),  # Mocked
                member_id=uuid4(),
                watcher_domain=self.domain,
                signal_date=datetime.now(timezone.utc).date(),
                signal_type=SignalType.TREND_CHANGE,
                severity=SignalSeverity.HIGH,
                signal_payload={"sleep_duration": value, "threshold": 5.0},
                deviation_from_baseline=-2.0,
                trend_direction=TrendDirection.DECLINING,
                supporting_data={"days_poor_sleep": 3},
                surfaced=False,
                expires_at=None,
                created_at=datetime.now(timezone.utc),
            )
            # We would normally save this signal via self.signal_repo.save()
            return signal
        return None
