import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from core.services.clinical_rules_engine import ClinicalRulesEngine
from core.services.confidence_calculator import ConfidenceCalculator
from infrastructure.database.models import DomainConfidence

def test_clinical_rules_engine_deterministic():
    engine = ClinicalRulesEngine()
    
    # Test diabetes
    interval = engine.determine_follow_up("diabetes", "diagnosis")
    assert interval == timedelta(days=90)
    
    # Test hypertension
    interval = engine.determine_follow_up("high blood pressure", "diagnosis")
    assert interval == timedelta(days=30)
    
    # Test generic medication
    interval = engine.determine_follow_up("Lisinopril", "medication")
    assert interval == timedelta(days=14)
    
    # Test unknown diagnosis fallback
    interval = engine.determine_follow_up("unknown rare disease", "diagnosis")
    assert interval is None

def test_confidence_calculator_decay():
    calc = ConfidenceCalculator()
    now = datetime.now(timezone.utc)
    
    # Mock a domain confidence record that is 2 weeks old
    two_weeks_ago = now - timedelta(days=14)
    record = DomainConfidence(
        family_id=uuid4(),
        member_id=uuid4(),
        domain="cardiology",
        completeness=1.0,
        freshness=1.0,
        confidence=0.9,
        evidence_count=5,
        last_updated=two_weeks_ago
    )
    
    # Default decay is 10% (0.1) per week. 2 weeks = 20% (0.2) decay.
    # Freshness should drop from 1.0 to 0.8.
    new_freshness = calc.calculate_current_freshness(record, memory_type="default")
    assert abs(new_freshness - 0.8) < 0.01

def test_confidence_calculator_update():
    calc = ConfidenceCalculator()
    now = datetime.now(timezone.utc)
    
    record = DomainConfidence(
        family_id=uuid4(),
        member_id=uuid4(),
        domain="cardiology",
        completeness=0.5,
        freshness=0.5,
        confidence=0.5,
        evidence_count=2,
        last_updated=now - timedelta(days=7)
    )
    
    # New evidence with high confidence (0.9)
    calc.update_domain_confidence(record, new_evidence_confidence=0.9, memory_type="diagnosis")
    
    # Freshness should be fully restored to 1.0
    assert record.freshness == 1.0
    # Evidence count incremented
    assert record.evidence_count == 3
    # Confidence should be a weighted moving average
    # Old = 0.5, New = 0.9. Formula: (0.5 * 0.7) + (0.9 * 0.3) = 0.35 + 0.27 = 0.62
    assert abs(record.confidence - 0.62) < 0.01
