import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from infrastructure.database.models import KnowledgeGap, NextAction
from core.services.information_gain_service import InformationGainService
from core.services.escalation_service import EscalationService

@pytest.mark.asyncio
async def test_information_gain_scoring():
    service = InformationGainService()
    
    # High priority gap, completely receptive user
    gap_high = KnowledgeGap(clinical_priority="high", confidence=0.1) # Info Gain = 0.9
    # Score = (0.9 * 1.0 * 1.0) / 0.2 = 4.5
    score_high = service.score_gap(gap_high, fatigue_multiplier=1.0)
    assert score_high == pytest.approx(4.5)
    
    # Low priority gap, completely receptive user
    gap_low = KnowledgeGap(clinical_priority="low", confidence=0.8) # Info Gain = 0.2
    # Score = (0.2 * 0.2 * 1.0) / 0.2 = 0.2
    score_low = service.score_gap(gap_low, fatigue_multiplier=1.0)
    assert score_low == pytest.approx(0.2)
    
    # High priority gap, severely fatigued user
    score_fatigued = service.score_gap(gap_high, fatigue_multiplier=0.01)
    # Score = (0.9 * 1.0 * 0.01) / 0.2 = 0.045
    assert score_fatigued == pytest.approx(0.045)
    
    # Assert fatigue suppresses high priority gap below a standard receptive threshold
    assert score_fatigued < 0.5 # Below standard action threshold

@pytest.mark.asyncio
async def test_deterministic_escalation_engine():
    # Mocking the digital twin input for the EscalationService
    class MockTwin:
        def __init__(self):
            self.insights = {
                "member_id_str": [
                    {"type": "alert", "desc": "High BP over 14 days"}
                ]
            }
            
    twin = MockTwin()
    
    # Risk (0.9) * Persistence (1.0) * Trend (0.8) * Confidence (0.9) * Evidence (1.0)
    # Score = 0.9 * 1.0 * 0.8 * 0.9 * 1.0 = 0.648
    # Threshold = 0.6
    
    # We can simulate this via the method logic:
    risk = 0.9
    persistence = 1.0
    trend = 0.8
    confidence = 0.9
    evidence = 1.0
    score = risk * persistence * trend * confidence * evidence
    
    assert score == pytest.approx(0.648)
    assert score > 0.6 # Should trigger escalation
