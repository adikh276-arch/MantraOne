from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from core.domain.enums import WatcherDomain, UrgencyLevel, TrendDirection, SignalSeverity


@dataclass(frozen=True)
class HealthBaseline:
    member_id: UUID
    domain: WatcherDomain
    baseline_data: dict
    confidence_score: float
    data_points_count: int
    calculated_at: datetime

    def has_sufficient_data(self) -> bool:
        return self.data_points_count >= 14 and self.confidence_score >= 0.5

    def get_metric(self, key: str, default: float = 0.0) -> float:
        return float(self.baseline_data.get(key, default))


@dataclass(frozen=True)
class ConvergenceResult:
    domains_involved: tuple[WatcherDomain, ...]
    convergence_score: float
    urgency_level: UrgencyLevel
    time_window_days: int
    triggering_signals: tuple[dict, ...]

    def meets_threshold(self) -> bool:
        return len(self.domains_involved) >= 2

    def to_dict(self) -> dict:
        return {
            "domains_involved": [d.value for d in self.domains_involved],
            "convergence_score": self.convergence_score,
            "urgency_level": self.urgency_level.value,
            "time_window_days": self.time_window_days,
            "triggering_signals": list(self.triggering_signals),
        }


@dataclass(frozen=True)
class DomainSignalSummary:
    domain: WatcherDomain
    signal_count: int
    max_severity: SignalSeverity
    avg_deviation: float
    trend_direction: TrendDirection

    @property
    def is_concerning(self) -> bool:
        return self.max_severity >= SignalSeverity.HIGH or self.trend_direction == TrendDirection.DECLINING
